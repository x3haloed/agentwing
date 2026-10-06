#!/usr/bin/env python3
"""Independent AW-0178 raw-hash, shape, finite-value and common-prefix gate replay."""
import argparse,json
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,digest
R=Path('/Users/chad/Models/agentwing/evidence/AW-0178')

def audit(partial=False):
 plan=json.loads((R/'plan.json').read_text())
 assert digest(ROOT/'experiments/fixtures/bonsai-cache-factorial-replay.cpp')==plan['source_sha256']
 assert digest(ROOT/'scripts/run_bonsai_cache_factorial_replay.py')==plan['harness_sha256']
 assert digest(R/'replay')==plan['binary_sha256']
 assert digest(ROOT/'spec/bonsai-turbo-local.json')==plan['runtime_spec_sha256']
 for name,h in plan['headers'].items():assert digest(Path('/Users/chad/Models/agentwing/runtime-sources/prism-turbo-port')/name)==h
 for name,h in plan['runtime']['runtime']['libraries'].items():assert digest(Path('/Users/chad/Models/agentwing/runtime-builds/prism-turbo-server/bin')/name)==h
 for name,info in plan['inputs'].items():assert digest(Path('/Users/chad/Models/agentwing/evidence/AW-0144')/name)==info['sha256']
 verified={}
 for position,arm in plan['order']:
  directory=R/f'{position}-{arm}'
  if not (directory/'result.json').exists():
   if partial:continue
   raise AssertionError('Required arm not terminal')
  row=json.loads((directory/'result.json').read_text())
  actual={p.name:digest(p) for p in directory.iterdir() if p.is_file() and p.name!='result.json'}
  assert actual==row['raw_sha256']
  assert row['exit']==0 and row['error'] is None
  native=(directory/'native.log').read_text()
  allocation=next(l for l in native.splitlines() if 'K (' in l and 'V (' in l)
  assert '16384 cells' in allocation
  assert ('K (q8_0):' if arm in ['turbo','q8-f16'] else 'K (f16):') in allocation
  assert ('V (turbo4):' if arm in ['turbo','f16-turbo'] else 'V (f16):') in allocation
  samples=[l.split('\t') for l in (directory/'pressure.tsv').read_text().splitlines()]
  assert max(int(s[1]) for s in samples)==row['pressure_peak']<4
  assert row['swap_growth_peak_mib']<=1024
  lines=(directory/'capture.tsv').read_text().splitlines();tokens=[int(l.split('\t')[2]) for l in lines if l.startswith('TOKEN\t')];assert len(tokens)==32
  n=int(next(l.split('\t')[1] for l in lines if l.startswith('PROMPT_TOKENS\t')))
  assert (directory/'prompt-tokens.bin').stat().st_size==n*4
  data=np.fromfile(directory/'logits.bin',dtype='<f4');assert data.size==32*248320 and np.isfinite(data).all()
  captures=[l.split('\t') for l in lines if l[0].isdigit()];assert len(captures)==384
  assert {(int(c[0]),int(c[1])) for c in captures}=={(i,j) for i in range(192) for j in [0,1]}
  expected={'blk.0.ssm_out.weight','blk.0.ffn_down.weight','blk.31.attn_output.weight','blk.31.ffn_down.weight','blk.63.attn_output.weight','blk.63.ffn_down.weight'}
  assert {c[2] for c in captures}==expected
  for c in captures:
   f=directory/f'{c[0]}-{c[1]}.bin';assert f.stat().st_size==int(c[6]);values=np.fromfile(f,dtype='<f4');assert values.size==int(c[4])*int(c[5]) and np.isfinite(values).all()
  verified[(position,arm)]={'directory':directory,'row':row,'tokens':tokens,'logits':data.reshape(32,248320),'prompt_tokens':n}
 pairs=[]
 for arm in ['q8-f16','f16-turbo','turbo']:
  position=7695
  if (position,'f16') not in verified or (position,arm) not in verified:continue
  a=verified[(position,'f16')];b=verified[(position,arm)]
  assert digest(a['directory']/'prompt-tokens.bin')==digest(b['directory']/'prompt-tokens.bin')
  x=a['logits'][0].astype(np.float64);y=b['logits'][0].astype(np.float64)
  relative=float(np.linalg.norm(y-x)/max(np.linalg.norm(x),1e-30))
  topa=set(np.argsort(x,kind='stable')[-20:].tolist());topb=set(np.argsort(y,kind='stable')[-20:].tolist());overlap=len(topa&topb)/20
  common_prefix=next((i for i,(u,v) in enumerate(zip(a['tokens'],b['tokens'])) if u!=v),32)
  pairs.append({'candidate_arm':arm,'own32_common_token_prefix':common_prefix,'position_chunks':position,'prompt_tokens':a['prompt_tokens'],'first_row_relative_l2':relative,'first_row_top20_overlap':overlap,'numeric_gate_passed':relative<=.10 and overlap>=.50,'own32_token_matches':sum(x==y for x,y in zip(a['tokens'],b['tokens'])),'own_trajectory_scope':'Descriptive only; later logits have potentially different inputs','arm_result_sha256':{arm:digest(verified[(position,arm)]['directory']/'result.json') for arm in ['f16',arm]}})
 complete=len(verified)==4
 if complete:
  summary=json.loads((R/'execution-summary.json').read_text());assert summary['complete']
  assert [(r['position_chunks'],r['arm']) for r in summary['rows']]==[tuple(v) for v in plan['order']]
  assert all(r==verified[(r['position_chunks'],r['arm'])]['row'] for r in summary['rows'])
 return {'experiment':'AW-0178','complete':complete,'passed':complete and len(pairs)==3 and all(p['numeric_gate_passed'] for p in pairs),'verified_arms':len(verified),'pairs':pairs,'plan_sha256':digest(R/'plan.json'),'auditor_sha256':digest(Path(__file__)),'scope':'Provisional identical-prefix numeric falsifier, not endpoint/general-quality qualification'}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--partial',action='store_true');args=parser.parse_args();print(json.dumps(audit(args.partial),indent=2))
