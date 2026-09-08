"""Audit AW-0059 original-suite screen, including terminal negative results."""
import json
from pathlib import Path
import sys
from run_local_agent import ROOT, digest, preflight
from run_matched_navigation import protocol_audit
from verify_original_copy import SUITE, verify


def audit(run):
    receipt=json.loads((run/'sha256-recursive.json').read_text())
    actual={str(p.relative_to(run)) for p in run.rglob('*') if p.is_file() and p.name!='sha256-recursive.json'}
    assert actual==set(receipt)
    for rel,h in receipt.items():
        p=run/rel
        assert not p.is_symlink() and p.resolve().is_relative_to(run.resolve())
        assert digest(p)==h,rel
    record=json.loads((run/'manifest.json').read_text())
    summary=json.loads((run/'summary.json').read_text())
    plan=json.loads((run/'screen-plan.json').read_text())
    assert digest(run/'screen-plan.json')==record['screen_plan_sha256']==digest(ROOT/'evidence/AW-0059-screen-plan.json')
    for file,h in plan['pins'].items():
        assert digest(Path(file) if Path(file).is_absolute() else ROOT/file)==h,file
    for file,h in record['source_hashes'].items():
        assert digest(run/Path(file).name)==h==plan['pins'][file]
    candidate=json.loads((run/'candidate-plan.json').read_text()) if record['slot']=='A1' else None
    deps=json.loads((ROOT/'spec/dependencies.json').read_text())
    if candidate:
        assert digest(run/'candidate-plan.json')==record['candidate_plan_sha256']==plan['pins']['spec/joint-development-candidate.json']
        assert record['server_binary_sha256']==candidate['server_binary_sha256']==digest(candidate['server_binary'])
        for file,h in candidate['runtime_files'].items():assert digest(file)==h
        prefix=['/usr/bin/env',*[f'{k}={v}' for k,v in sorted(candidate['environment'].items())],candidate['server_binary']]
    else:
        assert record['slot'] in ['C1','C2'] and record['profile']=='P1' and record['candidate_plan_sha256'] is None
        prefix=[str(Path(deps['swiftlet']['local_path'])/'.build/release/swiftlet-server')]
        assert record['server_binary']==prefix[0] and record['server_binary_sha256']==digest(prefix[0])
    expected=prefix+['--model',deps['qwen3_6_35b_a3b_8bit_qpack']['local_path'],'--port','8080','--cache-gb','0.5','--debug-tool-output','--accept-schema-tags','--salvage-tool-prefix','--allow-repeated-ngrams','--stop-after-tool-call']
    assert record['server_command']==expected and not record['inherited_runtime_environment']
    assert record['task_timeout_seconds']==900
    for rel,h in record['original_suite_hashes'].items():assert digest(SUITE/rel)==h
    assert record['selection']==plan['selection']
    tasks=summary['tasks'];assert [t['task_id'] for t in tasks]==plan['selection'][:len(tasks)]
    checks=[]
    for row in tasks:
        d=run/row['task_id'];assert json.loads((d/'scored-result.json').read_text())==row
        assert protocol_audit(d)==row['protocol']
        grade=verify(row['task_id'],d/'workspace')
        assert grade['utility']==row['grading']['utility']
        assert grade['frozen_grader_report']==row['grading']['frozen_grader_report']
        report=json.loads((d/'result.json').read_text());assert report==row['execution']
        expected_utility=grade['utility'] if report['status']=='client-completed' and report['error'] is None and row['protocol']['passed'] else 0
        assert row['utility']==expected_utility
        assert digest(d/'system-prompt.txt')==plan['pins']['config/validated-local-agent-prompt.txt']
        assert digest(d/'pi-models.json')==plan['pins']['config/pi-models-validated.json']
        events=[json.loads(s) for s in (d/'pi.jsonl').read_text().splitlines()]
        sessions=[e for e in events if e['type']=='session'];assert len(sessions)==1 and sessions[0]['cwd']==record['workspace_policy']['path']
        original=next(t for t in json.loads((SUITE/'manifest.json').read_text())['tasks'] if t['id']==row['task_id'])
        assert (d/'task.txt').read_text()==original['prompt']
        samples=[s.split('\t') for s in (d/'pressure.tsv').read_text().splitlines()]
        assert samples and max(int(s[1]) for s in samples)<4 and report['swap_growth_peak_mib']<=1024
        checks.append({'task_id':row['task_id'],'utility':row['utility'],'protocol_passed':row['protocol']['passed'],'grader_replay_passed':True,'host_gates_passed':True})
    assert summary['utility']==sum(t['utility'] for t in tasks)
    assert summary['wall_seconds']>=sum(t['full_wall_seconds'] for t in tasks)
    if not summary['complete_selection']:
        assert summary['error']
    preflight()
    return {'run':str(run),'raw_receipt_sha256':digest(run/'sha256-recursive.json'),'record_integrity_passed':True,'tasks':checks,'unattempted':plan['selection'][len(tasks):],'wall_seconds':summary['wall_seconds'],'accepted_utility':summary['utility'],'slot':record['slot'],'complete_arm':summary['complete_selection'],'post_run_p1_preflight_passed':True,'scope':'Configuration, receipt, protocol and copied frozen-grader replay. Negative result cannot establish relative runtime regression without matched controls.'}

if __name__=='__main__':print(json.dumps(audit(Path(sys.argv[1])),indent=2))
