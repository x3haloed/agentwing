#!/usr/bin/env python3
"""Independent AW-0136 trace audit; numeric comparison diagnostic only."""
import json,math,struct,hashlib
from pathlib import Path
R=Path('/Users/chad/Models/agentwing/evidence/AW-0136');OLD=R.parent/'AW-0098'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def floats(p):return [x[0] for x in struct.iter_unpack('<f',Path(p).read_bytes())]
def relative(a,b):return math.sqrt(math.fsum((x-y)**2 for x,y in zip(a,b))/math.fsum(x*x for x in b))
def main():
 result=json.loads((R/'result.json').read_text());assert result['passed'];plan=json.loads((R/'plan.json').read_text());assert sha(R/'plan.json')==result['plan_sha256'];assert sha('experiments/fixtures/bonsai-turbo-model-generation.cpp')==plan['source_sha256']
 index=(R/'capture.tsv').read_text().splitlines();tokens=[line.split('\t') for line in index if line.startswith('TOKEN\t')];nodes=[line.split('\t') for line in index if not line.startswith('TOKEN\t')];assert len(tokens)==32 and len(nodes)==396;ids=[int(x[2]) for x in tokens];nv=int(tokens[0][3]);assert nv==248320 and all(int(x[3])==nv and int(x[1])==i for i,x in enumerate(tokens))
 old=next(x for x in json.loads((OLD/'run-hashes.json').read_text()) if x['directory'].endswith('/1-B'));assert ids==old['tokens'];refdir=Path(old['directory']);assert sha(refdir/'logits.bin')==old['files']['logits.bin']
 patterns=['blk.0.ssm_out.weight','blk.0.ffn_down.weight','blk.31.attn_output.weight','blk.31.ffn_down.weight','blk.63.attn_output.weight','blk.63.ffn_down.weight'];records=[];total=0
 for f in nodes:
  node,role=int(f[0]),int(f[1]);assert f[2]==patterns[node%6];p=R/f'{node}-{role}.bin';assert sha(p)==result['capture_files'][p.name]['sha256'];assert p.stat().st_size==int(f[6]);a=floats(p);assert all(math.isfinite(x) for x in a);total+=len(a)
  ref=refdir/p.name;assert sha(ref)==old['files'][p.name];b=floats(ref);assert len(a)==len(b);records.append({'node':node,'role':role,'weight':f[2],'relative_l2_diagnostic':relative(a,b)})
 logits=R/'logits.bin';assert logits.stat().st_size==32*nv*4;logit_errors=[]
 with logits.open('rb') as a,(refdir/'logits.bin').open('rb') as b:
  for i in range(32):
   aa=[x[0] for x in struct.iter_unpack('<f',a.read(nv*4))];bb=[x[0] for x in struct.iter_unpack('<f',b.read(nv*4))];assert all(math.isfinite(x) for x in aa);logit_errors.append(relative(aa,bb))
 log=(R/'native.log').read_text();assert 'K (q8_0):   34.00 MiB, V (turbo4):   17.00 MiB' in log and 'kernel_turbo_wht' in log
 audit={'experiment':'AW-0136','passed':True,'generated_tokens':32,'vocabulary':nv,'all_generated_ids_match_frozen_FP16_probe':True,'selected_nodes':198,'activation_files':396,'finite_activation_values':total,'finite_logit_values':32*nv,'observed_kv_mib':{'K_q8':34,'V_turbo4':17,'total':51,'context':2048,'full_attention_layers':16},'max_activation_relative_l2_diagnostic':max(x['relative_l2_diagnostic'] for x in records),'max_logits_relative_l2_diagnostic':max(logit_errors),'activation_records':records,'logit_errors':logit_errors,'logits_sha256':sha(logits),'generated_text_sha256':sha(R/'generated.txt'),'reference_manifest_sha256':sha(OLD/'run-hashes.json'),'limitations':'Single raw32-token native probe, no endpoint quality/vision/long-context or speed qualification. Numeric differences diagnostic only, no posthoc numeric acceptance threshold.'};(R/'independent-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k not in ['activation_records','logit_errors']},indent=2))
if __name__=='__main__':main()
