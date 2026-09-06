#!/usr/bin/env python3
"""Audit one completed AW-0049 record; integrity is not candidate acceptance."""
import argparse
import json
from pathlib import Path
from audit_p2_development import audit
from run_local_agent import ROOT, digest


def check(run):
    plan_path = ROOT/'evidence/AW-0049-development-breadth-plan.json'
    plan = json.loads(plan_path.read_text())
    manifest = json.loads((run/'manifest.json').read_text())
    summary = json.loads((run/'summary.json').read_text())
    candidate = json.loads((ROOT/plan['candidate_plan']).read_text())
    settings = json.loads((ROOT/'spec/validated-local-agent.json').read_text())['settings']
    integrity = audit(run)
    checks = {
        'single_declared_task': len(manifest['selection']) == 1 and any(
            manifest['selection'] == [row['task']] and manifest['profile'] == row['profile']
            for row in plan['order']),
        'candidate_plan_pin': digest(ROOT/plan['candidate_plan']) == plan['candidate_plan_sha256']
            == manifest['candidate_plan_sha256'] == digest(run/'candidate-plan.json'),
        'server_binary_pin': manifest['server_binary_sha256'] == candidate['server_binary_sha256'],
        'runner_pin': digest(ROOT/plan['runner']) == plan['runner_sha256']
            == manifest['source_hashes'][plan['runner']] == digest(run/Path(plan['runner']).name),
        'workspace_helper_pin': digest(ROOT/'scripts/stable_workspace.py') == plan['workspace_helper_sha256']
            == manifest['source_hashes']['scripts/stable_workspace.py'] == digest(run/'stable_workspace.py'),
        'corpus_pin': manifest['corpus_receipt_sha256'] == plan['corpus_receipt_sha256'],
        'workspace_policy': manifest['workspace_policy'] == plan['workspace_policy'],
        'task_deadline': manifest['task_timeout_seconds'] == plan['task_timeout_seconds'],
        'no_inherited_overrides': not manifest['inherited_runtime_environment'],
    }
    prefix = ['/usr/bin/env', *[f'{k}={v}' for k,v in sorted(candidate['environment'].items())], candidate['server_binary']]
    checks['server_environment_and_binary'] = manifest['server_command'][:len(prefix)] == prefix
    task_checks = []
    for task in manifest['selection']:
        directory = run/task
        events = [json.loads(line) for line in (directory/'pi.jsonl').read_text().splitlines() if line.strip()]
        sessions = [event for event in events if event.get('type') == 'session']
        task_checks.append({'task': task,
            'actual_cwd': len(sessions) == 1 and sessions[0]['cwd'] == plan['workspace_policy']['path'],
            'prompt_pin': digest(directory/'system-prompt.txt') == settings['system_prompt_sha256'],
            'models_pin': digest(directory/'pi-models.json') == settings['pi_models_sha256'],
            'archived_workspace_and_state': (directory/'workspace').is_dir() and (directory/'agentwing-task-state').is_dir()})
    passed = integrity['passed'] and all(checks.values()) and all(
        all(v for k,v in row.items() if k != 'task') for row in task_checks)
    return {'run': str(run), 'plan_sha256': digest(plan_path),
            'raw_receipt_sha256': digest(run/'sha256-recursive.json'),
            'integrity': integrity, 'checks': checks, 'task_checks': task_checks,
            'passed': passed, 'accepted_utility': summary['utility'],
            'protocol_passed': all(row['protocol']['passed'] for row in summary['tasks']),
            'scope': 'Record integrity and frozen configuration checks. A zero-utility or protocol-failed record may pass integrity; no speedup or promotion claim.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    result = check(parser.parse_args().run)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
