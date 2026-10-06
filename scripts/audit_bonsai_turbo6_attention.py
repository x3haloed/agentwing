#!/usr/bin/env python3
"""AW208 independent packed-value inverse and scalar-fsum attention audit."""
import json,re,math,statistics
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,digest
R=Path('/Users/chad/Models/agentwing/evidence/AW-0208')
def main():
 result=json.loads((R/'result.json').read_text());plan=json.loads((R/'plan.json').read_text());assert digest(R/'plan.json')==result['plan_sha256']
 for name,sha in plan['inputs_sha256'].items():assert digest(R/name)==sha
 source=(ROOT/'experiments/fixtures/bonsai-precision-codec.cpp').read_text();signs=[np.array([float(v) for v in re.search(r'turbo_cpu_s'+str(k)+r'\[128\] = \{([^}]+)',source)[1].split(',')]) for k in [1,2]];books=json.loads((R.parent/'AW-0199/result.json').read_text())['tables'];checked={};records=[];peak=0;growth=0;minfree=None
 for row in result['rows']:
  i,layer,arm,nq,mode=row['index'],row['layer'],row['arm'],row['n_queries'],row['mode'];d=R/f'{layer}-{mode}-{nq}-{arm}';out=R/f'{i}-output.bin';log=R/f'{i}-native.log';assert digest(out)==row['output_sha256'] and digest(log)==row['log_sha256'];bits=4 if arm=='control' else 6;key=(layer,mode,arm)
  if key not in checked:
   size=4+16*bits;packed=(d/'v.bin').read_bytes();centers=np.array(books[str(bits)]['centroids'],dtype=np.float32).astype(float);v=np.empty((512,128))
   for b in range(512):
    block=packed[b*size:(b+1)*size];assert block[2:4]==b'\0\0';scale=float(np.frombuffer(block[:2],dtype='<f2')[0]);payload=int.from_bytes(block[4:],'little');ids=[(payload>>(j*bits))&((1<<bits)-1) for j in range(128)];v[b]=centers[ids]*scale*signs[1]
   for h in [1,2,4,8,16,32,64]:
    for start in range(0,128,2*h):
     a=v[:,start:start+h].copy();b=v[:,start+h:start+2*h].copy();v[:,start:start+h]=a+b;v[:,start+h:start+2*h]=a-b
   v*=signs[0]/math.sqrt(128);v=v.reshape(4,64,256);q=np.fromfile(d/'q.bin',dtype='<f4').reshape(24,nq,256)[:,0].astype(float)
   if mode=='f16-turbo':k=np.fromfile(d/'k.bin',dtype='<f2').reshape(4,64,256).astype(float)
   else:
    raw=np.fromfile(d/'k.bin',dtype=np.uint8).reshape(-1,34);scales=raw[:,:2].copy().view('<f2').reshape(-1).astype(float);k=(raw[:,2:].copy().view(np.int8).astype(float)*scales[:,None]).reshape(4,64,256)
   expected=[]
   for head in range(24):
    scores=[math.fsum(float(k[head//6,t,j])*float(q[head,j]) for j in range(256))*.0625 for t in range(48)];ex=[math.exp(x-max(scores)) for x in scores];den=math.fsum(ex);w=[x/den for x in ex];expected.extend(math.fsum(w[t]*float(v[head//6,t,j]) for t in range(48)) for j in range(256))
   checked[key]=np.array(expected)
  independent=np.tile(checked[key],nq);oracle=np.fromfile(d/'oracle.bin',dtype='<f8');oracle_error=float(np.linalg.norm(independent-oracle)/np.linalg.norm(independent));assert oracle_error<5e-7
  x=np.fromfile(out,dtype='<f4').astype(float);assert x.shape==independent.shape and np.isfinite(x).all();error=float(np.linalg.norm(x-independent)/np.linalg.norm(independent));assert error<=.005
  trace=np.loadtxt(R/f'{i}-pressure.tsv',ndmin=2);assert len(trace)>0 and max(trace[:,1])<4;g=max(0,float(max(trace[:,2]))-row['baseline_swap_mib']);assert g<=1024;peak=max(peak,float(max(trace[:,1])));growth=max(growth,g);capacity=np.loadtxt(R/f'{i}-capacity.tsv',ndmin=2);f=float(min(capacity[:,1]));assert f>=8*1024**3;minfree=f if minfree is None else min(minfree,f)
  timings=[float(z) for z in re.findall(r'compute_readback_seconds=([\d.]+)',log.read_text())];assert len(timings)==5 and statistics.median(timings[1:])==row['steady_median_seconds'];kind='_vec' if nq==1 else '';kt='kf16' if mode=='f16-turbo' else 'kq8_0';assert f'kernel_flash_attn_ext{kind}_{kt}_vturbo{bits}_dk256_dv256' in log.read_text();assert row['exit']==0 and not row['error'];records.append({'index':i,'independent_relative_l2':error,'oracle_independent_relative_l2':oracle_error})
 assert len(records)==48
 for pair in result['pairs']:
  a,b=result['rows'][pair['candidate_index']],result['rows'][pair['control_index']];assert a['steady_median_seconds']/b['steady_median_seconds']==pair['cost_ratio'] and pair['cost_ratio']<=1.10;assert a['uncompressed_attention_relative_l2']<b['uncompressed_attention_relative_l2']
 audit={'experiment':'AW-0208','passed':True,'result_sha256':digest(R/'result.json'),'auditor_sha256':digest(Path(__file__)),'sign_source_sha256':digest(ROOT/'experiments/fixtures/bonsai-precision-codec.cpp'),'book_authority_sha256':digest(R.parent/'AW-0199/result.json'),'records':records,'pressure_peak':peak,'swap_growth_peak_mib':growth,'minimum_free_bytes':minfree,'raw_sha256':{str(p.relative_to(R)):digest(p) for p in R.rglob('*') if p.is_file()},'scope':'Independent float64 WHT/bit decode/fsum attention, hashes, selected kernel and host/capacity replay; replicated128query shape, not causal full prefill or model endpoint.'};(R/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k not in ['records','raw_sha256']},indent=2))
if __name__=='__main__':main()
