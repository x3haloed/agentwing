#!/usr/bin/env python3
"""AW212 independent partial/full functional and reviewed-tool replay."""
import argparse,json
from pathlib import Path
from run_local_agent import ROOT,digest
from run_bonsai_budget_debugging_v2 import protocol
R=Path('/Users/chad/Models/agentwing/evidence/AW-0212')
def main(partial):
 plan=json.loads((R/'plan.json').read_text());review=json.loads((R/'tool-review.json').read_text());records=[]
 for n,h in plan['pins'].items():assert digest(ROOT/n)==h
 for n,h in plan['configuration']['runtime']['libraries'].items():assert digest(Path(plan['configuration']['runtime']['server_path']).parent/n)==h
 assert digest(R/'source-fixture.txt')==plan['source_fixture_sha256']
 for i,arm in enumerate(plan['order']):
  d=R/f'{i}-{arm}'
  if not (d/'result.json').exists():
   assert partial;continue
  row=json.loads((d/'result.json').read_text());assert row['passed'] and row['client_exit']==row['server_exit_after_cleanup']==0
  for n,h in json.loads((d/'sha256.json').read_text()).items():assert digest(d/n)==h
  assert (d/'pi-workspace/source.txt').read_bytes()==(d/'pi-workspace/answer.txt').read_bytes()==(R/'source-fixture.txt').read_bytes();pa=protocol(d);assert pa['passed'];a=review[str(i)];assert a['commands']==pa['commands'] and a['pi_jsonl_sha256']==digest(d/'pi.jsonl');account=a['accounting'];assert account['attempted']==account['valid']==len(pa['commands']);assert account['productive']+account['redundant']==account['attempted'];assert account['failed']==pa['tool_accounting']['failed']==0
  pi=json.loads((d/'pi-result.json').read_text());assert pi['passed'];prompt=pi['command'][pi['command'].index('--system-prompt')+1];assert prompt=='Host platform: macOS (Darwin). Shell utilities are the macOS versions. Use bash to complete the task in the current directory. After verifying the output, stop.'
  samples=[json.loads(l) for l in (d/'pressure.jsonl').read_text().splitlines()];assert max(s['pressure'] for s in samples)<4 and max(s['swap_mib']-row['baseline_swap_mib'] for s in samples)<=1024 and min(s['free_bytes'] for s in samples)>=8*1024**3
  cmd=json.loads((d/'command.json').read_text());assert cmd[cmd.index('--cache-type-v')+1]==('f16' if arm=='f16' else 'turbo6');assert cmd[cmd.index('--cache-type-k')+1]==('f16' if arm=='f16' else 'q8_0');assert cmd[cmd.index('--ctx-size')+1]=='16384' and cmd[cmd.index('--host')+1]=='127.0.0.1'
  records.append({'index':i,'arm':arm,'result_sha256':digest(d/'result.json'),'protocol':pa,'reviewed_tool_accounting':account,'pressure_peak':max(s['pressure'] for s in samples),'swap_growth_peak_mib':max(0,max(s['swap_mib']-row['baseline_swap_mib'] for s in samples)),'minimum_free_bytes':min(s['free_bytes'] for s in samples),'wall_seconds_diagnostic':row['wall_seconds_diagnostic']})
 result={'experiment':'AW-0212','complete':len(records)==4,'passed':len(records)==4,'records':records,'plan_sha256':digest(R/'plan.json'),'review_sha256':digest(R/'tool-review.json'),'auditor_sha256':digest(Path(__file__)),'scope':'Pi-only functional/cache screen, not complete multimodal/endpoint/causalprompt qualification'};(R/('partial-audit.json' if partial else 'terminal-audit.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--partial',action='store_true');args=p.parse_args();main(args.partial)
