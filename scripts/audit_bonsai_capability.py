#!/usr/bin/env python3
"""Independently audit a terminal frozen Bonsai original-task diagnostic."""
import argparse
import json
from pathlib import Path
from run_local_agent import ROOT, digest
from run_bonsai_capability import protocol
from verify_original_copy import SUITE as ORIGINAL_SUITE, verify as verify_original
from verify_p2_task import SUITE as EXPANDED_SUITE, verify as verify_expanded


def audit(run):
    summary=json.loads((run/'summary.json').read_text())
    manifest=json.loads((run/'manifest.json').read_text())
    receipt=json.loads((run/'sha256-recursive.json').read_text())
    actual={str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and p.name!='sha256-recursive.json'}
    assert receipt==actual,'Raw evidence receipt differs'
    plan=json.loads((run/'plan.json').read_text());assert digest(run/'plan.json')==manifest['plan_sha256']
    for name,sha in plan['pins'].items():
        assert digest(ROOT/name)==sha, f'Frozen source/input changed: {name}'
        snapshot=run/'source-snapshot'/name
        if snapshot.exists():assert digest(snapshot)==sha, f'Source snapshot changed: {name}'
    expanded=plan.get('suite_kind') in {'p2-development','p2-development-falsifier'}
    SUITE=EXPANDED_SUITE if expanded else ORIGINAL_SUITE
    verify=verify_expanded if expanded else verify_original
    check_protocol=protocol
    if not expanded and plan.get('protocol_version')=='bounded-bash-v2':
        from run_bonsai_budget_debugging_v2 import protocol as check_protocol
    if expanded:
        if plan['suite_kind']=='p2-development-falsifier':
            if plan.get('protocol_version')=='bounded-bash-v2':
                from run_bonsai_budget_debugging_v2 import protocol as check_protocol
            else:
                from run_bonsai_budget_debugging import protocol as check_protocol
        else:
            from run_bonsai_development import protocol as check_protocol
    tasks=json.loads((SUITE/'manifest.json').read_text())['tasks']
    if expanded:
        if plan['suite_kind']=='p2-development-falsifier':
            assert plan['selection']==['dev-debugging']
            assert next(t for t in tasks if t['id']=='dev-debugging')['split']=='development'
        else:
            assert plan['selection']==[t['id'] for t in tasks if t['split']=='development']
    assert len(set(plan['selection']))==len(plan['selection'])
    assert plan['selection']==[t['id'] for t in tasks if t['id'] in plan['selection']]
    assert plan['successes_required']==len(plan['selection'])
    rows=summary['tasks'];assert [r['task_id'] for r in rows]==plan['selection'][:len(rows)]
    checked=[]
    for row in rows:
        directory=run/row['task_id']
        assert json.loads((directory/'scored-result.json').read_text())==row
        audit_protocol=check_protocol(directory);assert audit_protocol==row['protocol']
        grading=verify(row['task_id'],directory/'workspace');assert grading['utility']==row['grading']['utility']
        execution=row['execution']
        assert json.loads((directory/'result.json').read_text())==execution
        good=execution['status']=='client-completed' and execution['error'] is None and audit_protocol['passed']
        utility=grading['utility'] if good else 0
        assert utility==row['utility']
        samples=[line.split('\t') for line in (directory/'pressure.tsv').read_text().splitlines()]
        assert max(int(s[1]) for s in samples)==execution['pressure_peak']
        host_pass=execution['pressure_peak']<4 and execution['swap_growth_peak_mib']<=1024
        if utility:assert host_pass
        assert row['full_wall_seconds']>=execution['wall_seconds']
        test_integrity={str(f.relative_to(SUITE/'tasks'/row['task_id']/'input')): (directory/'workspace'/f.relative_to(SUITE/'tasks'/row['task_id']/'input')).is_file() and digest(f)==digest(directory/'workspace'/f.relative_to(SUITE/'tasks'/row['task_id']/'input')) for f in (SUITE/'tasks'/row['task_id']/'input').rglob('test_*.py')}
        checked.append({'original_test_file_integrity':test_integrity,'task_id':row['task_id'],'utility':utility,'grade_replay_matches':True,
                        'protocol_passed':audit_protocol['passed'],'host_passed':host_pass,
                        'full_wall_seconds':row['full_wall_seconds'],'pressure_peak':execution['pressure_peak'],
                        'swap_growth_peak_mib':execution['swap_growth_peak_mib'],'tool_accounting':audit_protocol['tool_accounting'],
                        'commands':audit_protocol['commands']})
    assert summary['unattempted']==plan['selection'][len(rows):]
    if plan['stop_on_first_failure'] and any(row['utility']!=1 for row in rows):assert rows[-1]['utility']==0 and summary['error']
    assert summary['complete']==(len(rows)==len(plan['selection']) and summary['error'] is None)
    utility=sum(r['utility'] for r in rows);assert utility==summary['utility']
    assert summary['wall_seconds']>=sum(r['full_wall_seconds'] for r in rows)
    assert abs(summary['diagnostic_utility_per_hour']-3600*utility/summary['wall_seconds'])<1e-9
    return {'audit_passed':True,'run':str(run),'raw_receipt_sha256':digest(run/'sha256-recursive.json'),
            'plan_sha256':manifest['plan_sha256'],'complete_selection':summary['complete'],
            'all_selected_tasks_passed':summary['complete'] and utility==len(plan['selection']),
            'screen_passed':summary['complete'] and utility==len(plan['selection']),
            'utility':utility,'wall_seconds':summary['wall_seconds'],'diagnostic_utility_per_hour':summary['diagnostic_utility_per_hour'],
            'unattempted':summary['unattempted'],'error':summary['error'],'tasks':checked,
            'supplemental_original_tests_unchanged':all(all(t['original_test_file_integrity'].values()) for t in checked),
            'scope':plan['scope'],'accounting_limit':'Summary timing excludes final recursive receipt creation; not promotion accounting.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);args=p.parse_args()
    print(json.dumps(audit(args.run.resolve()),indent=2))


if __name__=='__main__':main()
