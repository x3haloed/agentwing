#!/usr/bin/env python3
"""AW-0048 audit three completed, pinned development arms without promotion."""
import argparse
import datetime
import json
from pathlib import Path
from audit_p2_development import audit
from run_local_agent import ROOT,digest

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',required=True,choices=['dev-recovery']);parser.add_argument('runs',nargs=3,type=Path);args=parser.parse_args()
    plan=json.loads((ROOT/'evidence/AW-0048-fixed-workspace-plan.json').read_text())
    candidate=json.loads((ROOT/'spec/joint-development-candidate.json').read_text())
    settings=json.loads((ROOT/'spec/validated-local-agent.json').read_text())['settings']
    assert digest(ROOT/'spec/joint-development-candidate.json')==plan['candidate_plan_sha256']
    assert digest(ROOT/'scripts/run_stable_development.py')==plan['runner_sha256']
    assert digest(ROOT/'scripts/stable_workspace.py')==plan['workspace_helper_sha256']
    order=[row for row in plan['order'] if row['task']==args.task]
    assert len(order)==3
    rows=[];commands=[];starts=[]
    for expected,run in zip(order,args.runs):
        integrity=audit(run);assert integrity['passed'],integrity
        manifest=json.loads((run/'manifest.json').read_text());summary=json.loads((run/'summary.json').read_text())
        assert manifest['profile']==expected['profile'] and manifest['selection']==[args.task]
        assert manifest['corpus_receipt_sha256']==plan['corpus_receipt_sha256']
        assert manifest['source_hashes']['scripts/run_stable_development.py']==plan['runner_sha256']
        assert manifest['task_timeout_seconds']==1800 and not manifest['inherited_runtime_environment']
        assert manifest['workspace_policy']==plan['workspace_policy']
        assert manifest['source_hashes']['scripts/stable_workspace.py']==plan['workspace_helper_sha256']
        assert digest(run/'stable_workspace.py')==plan['workspace_helper_sha256']
        assert digest(run/'run_stable_development.py')==plan['runner_sha256']
        directory=run/args.task
        events=[json.loads(line) for line in (directory/'pi.jsonl').read_text().splitlines() if line.strip()]
        sessions=[event for event in events if event.get('type')=='session']
        assert len(sessions)==1 and sessions[0]['cwd']==plan['workspace_policy']['path']
        assert (directory/'workspace').is_dir() and (directory/'agentwing-task-state').is_dir()
        assert digest(directory/'system-prompt.txt')==settings['system_prompt_sha256']
        assert digest(directory/'pi-models.json')==settings['pi_models_sha256']
        command=manifest['server_command']
        if expected['arm']=='A1':
            assert manifest['candidate_plan_sha256']==plan['candidate_plan_sha256']
            assert digest(run/'candidate-plan.json')==plan['candidate_plan_sha256']
            assert manifest['server_binary_sha256']==candidate['server_binary_sha256']
            prefix=['/usr/bin/env',*[f'{k}={v}' for k,v in sorted(candidate['environment'].items())],candidate['server_binary']]
            assert command[:len(prefix)]==prefix
            commands.append(command[len(prefix):])
        else:
            assert manifest['candidate_plan_sha256'] is None
            assert manifest['server_binary_sha256']==settings['server_binary_sha256']
            commands.append(command[1:])
        starts.append(datetime.datetime.strptime(run.name,'%Y%m%dT%H%M%S.%fZ').replace(tzinfo=datetime.timezone.utc).timestamp())
        task=summary['tasks'][0]
        rows.append({'arm':expected['arm'],'run':str(run),'raw_receipt_sha256':digest(run/'sha256-recursive.json'),'integrity_audit':integrity,'utility':summary['utility'],'wall_seconds':summary['wall_seconds'],'utility_per_hour':summary['verified_utility_per_hour'],'task_protocol':task['protocol'],'grading':task['grading'],'server_binary_sha256':manifest['server_binary_sha256']})
    assert commands[0]==commands[1]==commands[2]
    assert rows[0]['server_binary_sha256']==rows[2]['server_binary_sha256']
    assert all(starts[i]+rows[i]['wall_seconds']<=starts[i+1] for i in [0,1]),'overlapping or misordered arms'
    pooled_control_rate=(rows[0]['utility']+rows[2]['utility'])*3600/(rows[0]['wall_seconds']+rows[2]['wall_seconds'])
    result={'plan_sha256':digest(ROOT/'evidence/AW-0048-fixed-workspace-plan.json'),'arms':rows,'pooled_control_utility_per_hour':pooled_control_rate,'candidate_to_control_utility_rate_ratio':rows[1]['utility_per_hour']/pooled_control_rate if pooled_control_rate else None,'candidate_preserves_control_success':rows[1]['utility']>=max(rows[0]['utility'],rows[2]['utility']),'candidate_protocol_passed':rows[1]['task_protocol']['passed'],'candidate_wall_ratio_to_neighbor_control_mean':rows[1]['wall_seconds']/((rows[0]['wall_seconds']+rows[2]['wall_seconds'])/2),'limits':['One frozen development task per audit; no broad capability or promotion claim','Elapsed-time ratio is not a speedup if utility is zero or protocol fails','Control-success preservation is vacuous when both controls score zero','A zero control utility rate has no finite comparison ratio','Live workspace and private-state paths are fixed; cache state and unrecorded wire spellings can still vary','Static admission checks precede the timed runner clock; this is not the full promotion accounting runner']}
    print(json.dumps(result,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
