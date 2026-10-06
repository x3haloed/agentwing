#!/usr/bin/env python3
"""Independent AW-0099 functional receipt/protocol replay, not utility scoring."""
import hashlib,json,re
from pathlib import Path
from run_bonsai_budget_debugging_v2 import protocol
from run_local_agent import ROOT,digest
PLAN=ROOT/'evidence/AW-0099-multimodal-plan.json'
R=Path('/Users/chad/Models/agentwing/evidence/AW-0099')
def main():
 plan=json.loads(PLAN.read_text())
 for name,h in plan['pins'].items():assert digest(ROOT/name)==h
 for name,h in plan['runtime_libraries'].items():assert digest(ROOT/'var/bonsai-demo/bin/mac'/name)==h
 records=[]
 for rep in range(2):
  candidates=[p for p in R.glob(f'*-rep{rep}') if (p/'result.json').exists() and (p/'plan.json').read_bytes()==PLAN.read_bytes()];assert len(candidates)==1
  run=candidates[0];result=json.loads((run/'result.json').read_text());assert result['passed']
  for name,h in json.loads((run/'sha256.json').read_text()).items():assert digest(run/name)==h
  cmd=json.loads((run/'command.json').read_text());assert cmd[cmd.index('--host')+1]=='127.0.0.1';assert cmd[cmd.index('--ctx-size')+1]=='16384';assert '--mmproj' in cmd and '--no-context-shift' in cmd;assert cmd[cmd.index('--cache-ram')+1]=='0' and cmd[cmd.index('--ctx-checkpoints')+1]=='2'
  text=json.loads((run/'text.json').read_text());assert text['response']['choices'][0]['message']['content'].strip()=='42'
  vision=json.loads((run/'vision.json').read_text());observed=re.findall(r'\b(red|blue)\b',vision['response']['choices'][0]['message']['content'].lower());assert observed==(['red','blue'] if rep==0 else ['blue','red'])
  native=json.loads((run/'tool-selection.json').read_text());calls=native['response']['choices'][0]['message']['tool_calls'];assert len(calls)==1 and calls[0]['function']['name']=='lookup_local_code' and json.loads(calls[0]['function']['arguments'])=={'key':'orchard'}
  continuation=json.loads((run/'tool-continuation.json').read_text());toolmsg=next(m for m in continuation['request']['messages'] if m['role']=='tool');assert toolmsg['tool_call_id']==calls[0]['id'];assert toolmsg['content'] in continuation['response']['choices'][0]['message']['content']
  expected=('LOCAL-'+hashlib.sha256(str(run).encode()).hexdigest()[:12]+'\n').encode();assert (run/'pi-workspace/source.txt').read_bytes()==expected and (run/'pi-workspace/answer.txt').read_bytes()==expected;audit=protocol(run);assert audit['passed']
  commands=audit['commands'];events=[json.loads(l) for l in (run/'pi.jsonl').read_text().splitlines() if l.strip()];ends=[e for e in events if e.get('type')=='tool_execution_end'];assert not any(e.get('isError') for e in ends)
  records.append({'replicate':rep,'run':str(run),'result_sha256':digest(run/'result.json'),'wall_seconds':result['wall_seconds'],'pressure_peak':result['pressure_peak'],'swap_growth_peak_mib':result['swap_growth_peak_mib'],'vision_colors':observed,'native_tool_accounting':native['tool_accounting'],'pi_protocol':audit,'pi_commands':commands,'artifact_sha256':digest(run/'pi-workspace/answer.txt')})
 receipt={'experiment':'AW-0099','passed':True,'plan_sha256':digest(PLAN),'records':records,'auditor_sha256':digest(Path(__file__)),'canonical_protocol_sha256':digest(ROOT/'scripts/run_bonsai_budget_debugging_v2.py'),'scope':'Two independent full multimodal functional replicas; no endpoint or heldout comparison'}
 (R/'independent-admission-audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
