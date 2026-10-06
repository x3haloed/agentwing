#!/usr/bin/env python3
"""Independent AW-0196 full-request stream/hash audit; proposals never execute."""
import argparse,json
from pathlib import Path
from run_local_agent import ROOT,digest
R=Path('/Users/chad/Models/agentwing/evidence/AW-0196')

from audit_bonsai_rollback_full_request import stream

def audit(partial=False):
 plan=json.loads((R/'plan.json').read_text());assert digest(ROOT/'scripts/replay_bonsai_current_history.py')==plan['harness_sha256'];assert digest(ROOT/'spec/bonsai-stationary-local.json')==plan['runtime_spec_sha256']
 assert digest(ROOT/'scripts/audit_bonsai_rollback_full_request.py')==plan['strict_stream_auditor_sha256']
 assert digest(ROOT/'evidence/AW-0192-stationary-admission.json')==plan['functional_admission_sha256']
 assert digest(ROOT/'evidence/AW-0195-stationary-request-comparison.json')==plan['history_receipt_sha256']
 rows=[];request_hashes=set()
 for arm in plan['order']:
  d=R/arm
  if not (d/'result.json').exists():
   if partial:continue
   raise AssertionError('Arm not terminal')
  row=json.loads((d/'result.json').read_text());actual={p.name:digest(p) for p in d.iterdir() if p.is_file() and p.name!='result.json'};assert actual==row['raw_sha256']
  assert json.loads((d/'request.json').read_text())==plan['request'];request_hashes.add(digest(d/'request.json'))
  cmd=json.loads((d/'server-command.json').read_text());assert cmd[cmd.index('--ctx-size')+1]=='16384';assert cmd[cmd.index('--parallel')+1]=='1';assert '--no-context-shift' in cmd;assert cmd[cmd.index('--reasoning-effort')+1]=='medium'
  native=(d/'server.log').read_text();allocation=next(l for l in native.splitlines() if 'K (' in l and 'V (' in l);assert ('K (f16):' in allocation and 'V (f16):' in allocation) if arm=='f16' else ('K (q8_0):' in allocation and 'V (turbo4):' in allocation)
  response=stream(d/'response.sse');host=row['pressure_peak']<4 and row['swap_growth_peak_mib']<=1024
  rows.append({'arm':arm,'result_sha256':digest(d/'result.json'),'error':row['error'],'client_exit':row['client_exit'],'server_exit_after_cleanup':row['server_exit_after_cleanup'],'host_passed':host,'response':response,'wall_seconds_diagnostic':row['wall_seconds_diagnostic']})
 assert len(request_hashes)<=1
 complete=len(rows)==2
 if complete:assert json.loads((R/'summary.json').read_text())['rows']==[json.loads((R/arm/'result.json').read_text()) for arm in plan['order']]
 return {'experiment':'AW-0196','complete':complete,'rows':rows,'plan_sha256':digest(R/'plan.json'),'auditor_sha256':digest(Path(__file__)),'scope':'One full native request per cache arm; no proposal execution, task score, performance ratio or causal qualification'}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--partial',action='store_true');args=parser.parse_args();print(json.dumps(audit(args.partial),indent=2))
