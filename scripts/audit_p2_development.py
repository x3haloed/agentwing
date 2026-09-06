#!/usr/bin/env python3
"""Recheck completed P2 development evidence and replay independent graders."""
import argparse
import json
from pathlib import Path
from run_local_agent import digest
from run_p2_development import protocol_audit
from verify_p2_task import verify


def audit(run):
    receipt=json.loads((run/'sha256-recursive.json').read_text())
    current={str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and not p.is_symlink() and p.name!='sha256-recursive.json'}
    manifest=json.loads((run/'manifest.json').read_text());summary=json.loads((run/'summary.json').read_text())
    checks={'hashes_match':receipt==current,'complete_selection':summary['complete_selection'] and [r['task_id'] for r in summary['tasks']]==manifest['selection'],
            'development_only':all(t.startswith('dev-') for t in manifest['selection']),
            'utility_sum':summary['utility']==sum(r['utility'] for r in summary['tasks']),
            'utility_rate':abs(summary['verified_utility_per_hour']-3600*summary['utility']/summary['wall_seconds'])<1e-9,
            'wall_includes_tasks':summary['wall_seconds']>=sum(r['full_wall_seconds'] for r in summary['tasks'])}
    task_checks=[]
    for row in summary['tasks']:
        directory=run/row['task_id'];protocol=protocol_audit(directory);grading=verify(row['task_id'],directory/'workspace');execution=json.loads((directory/'result.json').read_text())
        accepted=execution['status']=='client-completed' and execution['error'] is None and protocol['passed']
        samples=[line.split('\t') for line in (directory/'pressure.tsv').read_text().splitlines()]
        task_checks.append({'task_id':row['task_id'],'protocol_recomputed':protocol==row['protocol'],
                            'grader_utility_replayed':grading['utility']==row['grading']['utility'],
                            'accepted_utility':row['utility']==(grading['utility'] if accepted else 0),
                            'execution_matches':execution==row['execution'],
                            'pressure_safe':bool(samples) and all(int(x[1])<4 for x in samples),
                            'reported_swap_safe':execution['swap_growth_peak_mib'] is not None and execution['swap_growth_peak_mib']<=1024})
    passed=all(checks.values()) and all(all(v for k,v in r.items() if k!='task_id') for r in task_checks)
    return {'run':str(run),'checks':checks,'tasks':task_checks,'passed':passed,'scope':'Evidence integrity and verifier replay, not paired promotion or sandbox certification'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args();r=audit(a.run);print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)
