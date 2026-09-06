#!/usr/bin/env python3
"""Compare completed AW-0047 visible prefixes, not unrecorded wire tokens."""
import copy
import json
from pathlib import Path
from run_local_agent import ROOT, digest

BASE=Path('/Users/chad/Models/agentwing/evidence/AW-0047')
RUNS=['20260906T091156.920519Z','20260906T093621.794299Z','20260906T094822.332630Z']

def main():
    records=[]
    for label,name in zip(['C1','A1','C2'],RUNS):
        run=BASE/name
        receipt=json.loads((run/'sha256-recursive.json').read_text())
        assert all(digest(run/p)==h for p,h in receipt.items())
        events=[json.loads(x) for x in (run/'dev-recovery/pi.jsonl').read_text().splitlines() if x.strip()]
        starts=[e for e in events if e.get('type')=='tool_execution_start']
        ends=[e for e in events if e.get('type')=='tool_execution_end']
        replies=[e['message']['content'] for e in events if e.get('type')=='message_end' and e.get('message',{}).get('role')=='assistant']
        visible=[]
        for content in replies[:7]:
            content=copy.deepcopy(content)
            for block in content:
                if block.get('type')=='toolCall':block.pop('id',None)
            visible.append(content)
        result_strings=[json.dumps(e.get('result'),sort_keys=True,ensure_ascii=False) for e in ends[:7]]
        normalized=[s.replace(str(run/'dev-recovery/workspace'),'<WORKSPACE>') for s in result_strings]
        records.append({'arm':label,'run':str(run),'receipt_sha256':digest(run/'sha256-recursive.json'),
            'commands':[e.get('args',{}).get('command') for e in starts[:8]],
            'visible_assistant_prefix':visible,'tool_results':result_strings,'path_normalized_results':normalized})
    checks={
        'first_seven_commands_equal':records[0]['commands'][:7]==records[1]['commands'][:7]==records[2]['commands'][:7],
        'first_seven_structured_assistant_contents_equal_ignoring_call_ids':records[0]['visible_assistant_prefix']==records[1]['visible_assistant_prefix']==records[2]['visible_assistant_prefix'],
        'first_six_tool_results_equal':records[0]['tool_results'][:6]==records[1]['tool_results'][:6]==records[2]['tool_results'][:6],
        'all_seven_tool_results_equal_after_only_workspace_path_replacement':records[0]['path_normalized_results']==records[1]['path_normalized_results']==records[2]['path_normalized_results'],
        'seventh_tool_result_differs_before_path_replacement':len({r['tool_results'][6] for r in records})>1,
        'eighth_commands_differ':len({r['commands'][7] for r in records})>1}
    assert all(checks.values()),checks
    result={'checks':checks,'arms':[{'arm':r['arm'],'run':r['run'],'receipt_sha256':r['receipt_sha256'],'eighth_command':r['commands'][7]} for r in records],
        'limits':['Structured visible transcript only; exact rendered request tokens and accepted raw reply spellings were not captured',
                  'Workspace paths differ immediately before first differing repair; this is a confounder, not isolated causal proof',
                  'No change to the failed candidate grade, completed controls or ongoing frozen comparison']}
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
