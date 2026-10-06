#!/usr/bin/env python3
"""Independent raw-hash/full-vocabulary AW160 rollback audit."""
import json
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,digest

def main():
 r=Path('/Users/chad/Models/agentwing/evidence/AW-0160')
 result=json.loads((r/'result.json').read_text());plan=json.loads((r/'execution-plan.json').read_text())
 execution_passed=result['error'] is None and result['exit']==0
 host_passed=result['pressure_peak'] is not None and result['pressure_peak']<4 and result['swap_growth_peak_mib']<=1024
 for name,h in result['raw_sha256'].items():assert digest(r/name)==h,name
 assert digest(ROOT/'scripts/run_bonsai_rollback_fidelity.py')==plan['harness_sha256']
 assert digest(ROOT/'experiments/fixtures/bonsai-rollback-fidelity.cpp')==plan['fixture_sha256']
 assert digest(r/'fixture')==plan['fixture_binary_sha256']
 log=(r/'native.log').read_text();rows=[]
 for accepted in range(3):
  if not all((r/f'{accepted}-{arm}.bin').exists() for arm in ['control','rollback']):
   rows.append({'accepted_drafts':accepted,'passed':False,'status':'missing-complete-pair'});continue
  for arm in range(2):assert f'accepted={accepted} arm={arm} rollback={3-accepted} vocab=248320' in log
  a=np.fromfile(r/f'{accepted}-control.bin',dtype='<f4').astype(np.float64)
  b=np.fromfile(r/f'{accepted}-rollback.bin',dtype='<f4').astype(np.float64)
  assert a.shape==b.shape==(248320,) and np.isfinite(a).all() and np.isfinite(b).all()
  relative=float(np.linalg.norm(a-b)/np.linalg.norm(a));overlap=len(set(np.argsort(a)[-20:])&set(np.argsort(b)[-20:]))
  top1=int(np.argmax(a))==int(np.argmax(b))
  rows.append({'accepted_drafts':accepted,'rejected_drafts':3-accepted,'relative_L2':relative,'max_absolute':float(np.max(np.abs(a-b))),'top20_overlap_count':overlap,'top1_equal':top1,'passed':relative<=.001 and overlap==20 and top1})
 audit={'experiment':'AW-0160','raw_hashes_valid':True,'results':rows,'execution_passed':execution_passed,'host_passed':host_passed,'passed':execution_passed and host_passed and all(x['passed'] for x in rows),'auditor_sha256':digest(Path(__file__)),'result_sha256':digest(r/'result.json'),'execution_plan_sha256':digest(r/'execution-plan.json'),'scope':'Early-prefix raw API rollback numeric gate only; partial pairs are diagnostic only, sampler/server protocol/late-context/end-to-end remain unproven.'}
 (r/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
 if not audit['passed']:raise SystemExit(1)

if __name__=='__main__':main()
