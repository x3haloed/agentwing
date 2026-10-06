#!/usr/bin/env python3
"""Preserve AW211 rejected zero-execution-error screen without trusting collector flag."""
import json
from pathlib import Path
from run_local_agent import ROOT,digest
from run_bonsai_budget_debugging_v2 import protocol
R=Path('/Users/chad/Models/agentwing/evidence/AW-0211');PLAN=ROOT/'evidence/AW-0211-multimodal-plan.json'
def main():
 plan=json.loads(PLAN.read_text());review=json.loads((R/'tool-review.json').read_text());rows=[]
 for rep in range(2):
  runs=[p for p in R.glob(f'*-rep{rep}') if (p/'result.json').exists() and (p/'plan.json').read_bytes()==PLAN.read_bytes()];assert len(runs)==1;run=runs[0]
  for name,sha in json.loads((run/'sha256.json').read_text()).items():assert digest(run/name)==sha
  events=[json.loads(l) for l in (run/'pi.jsonl').read_text().splitlines() if l.strip()];starts=[e for e in events if e.get('type')=='tool_execution_start'];ends=[e for e in events if e.get('type')=='tool_execution_end'];pa=protocol(run);assert pa['passed'];commands=[e['args']['command'] for e in starts];account=review[str(rep)]['accounting'];assert commands==review[str(rep)]['commands'];assert digest(run/'pi.jsonl')==review[str(rep)]['pi_jsonl_sha256'];assert len(starts)==len(ends)==account['attempted']==account['valid'];assert sum(bool(e.get('isError')) for e in ends)==account['failed'];assert account['productive']+account['redundant']==len(starts)
  assert (run/'pi-workspace/source.txt').read_bytes()==(run/'pi-workspace/answer.txt').read_bytes();samples=[json.loads(l) for l in (run/'pressure.jsonl').read_text().splitlines()];assert max(s['pressure'] for s in samples)<4 and max(s['swap_mib']-samples[0]['swap_mib'] for s in samples)<=1024 and min(s['free_bytes'] for s in samples)>=8*1024**3
  gates=json.loads((run/'gates.json').read_text());assert len(gates)==4 and all(x['passed'] for x in gates);native=json.loads((run/'tool-selection.json').read_text())['tool_accounting'];rows.append({'replicate':rep,'run':str(run),'collector_result':json.loads((run/'result.json').read_text()),'collector_sha256':digest(run/'result.json'),'protocol':pa,'native_tool_accounting':native,'reviewed_pi_tool_accounting':account,'artifact_correct':True,'zero_execution_error_gate_passed':account['failed']==0,'raw_manifest_sha256':digest(run/'sha256.json')})
 total={k:sum(row['reviewed_pi_tool_accounting'][k]+row['native_tool_accounting'][k] for row in rows) for k in ['attempted','valid','productive','redundant','malformed','denied','failed']}
 receipt={'experiment':'AW-0211','complete':True,'admission_passed':all(row['zero_execution_error_gate_passed'] for row in rows),'records':rows,'total_tool_accounting':total,'plan_sha256':digest(PLAN),'review_sha256':digest(R/'tool-review.json'),'strict_admission_audit_exit_code':1,'strict_audit_output_sha256':digest(R/'terminal-audit-output.txt'),'summarizer_sha256':digest(Path(__file__)),'disposition':'Reject current zero-execution-error admission screen; retain rawnegative and functional artifact/vision evidence, no wholeformat rejection','scope':'Protocol/permissions/resource gates pass and both artifacts correct; one redundant valid bash call fails macOS cat-A. Collector passed flag is insufficient. No endpoint utility claim.'};(R/'terminal-summary.json').write_text(json.dumps(receipt,indent=2)+'\n');(ROOT/'evidence/AW-0211-turbo6-admission-terminal.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'admission_passed':receipt['admission_passed'],'total_tool_accounting':total},indent=2))
if __name__=='__main__':main()
