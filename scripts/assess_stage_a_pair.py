#!/usr/bin/env python3
"""Check necessary promotion metrics for one audited full-suite pair."""
import argparse
import json
from pathlib import Path

from audit_stage_a import audit

ROOT = Path(__file__).resolve().parents[1]


def pair_checks(control, candidate, control_manifest, candidate_manifest, spec):
    gate = spec['promotion']
    task_ids = [task['id'] for task in json.loads(
        (ROOT / 'benchmarks/stage-a-v1/manifest.json').read_text())['tasks']]
    checks = {}
    for role, summary, manifest in [('control', control, control_manifest),
                                    ('candidate', candidate, candidate_manifest)]:
        checks[role + '_full_suite'] = (
            manifest['task_selection'] == 'all' and summary['status'] == 'completed'
            and [task['task_id'] for task in summary['tasks']] == task_ids)
        checks[role + '_recorded_loopback'] = manifest['bind'] == '127.0.0.1'
        checks[role + '_pressure'] = 0 < summary['pressure_peak'] < 4
        checks[role + '_swap'] = (summary['swap_peak_mib'] - summary['swap_used_mib_before']) * 1048576 <= spec['host_safety']['maximum_sustained_swap_growth_bytes']
        checks[role + '_positive_duration'] = summary['wall_seconds'] > 0
    checks['same_suite_timeout_tools_storage_os'] = all(
        control_manifest[key] == candidate_manifest[key] for key in (
            'suite_id', 'suite_sha256', 'task_timeout_seconds', 'tools', 'storage',
            'os_version', 'os_build'))
    checks['minimum_candidate_successes'] = candidate['utility'] >= gate['minimum_candidate_task_success_count']
    checks['preserved_control_successes'] = candidate['utility'] >= control['utility']
    cr = 3600 * control['utility'] / max(1, control['wall_seconds'])
    ar = 3600 * candidate['utility'] / max(1, candidate['wall_seconds'])
    checks['historical_floor_rate'] = ar >= gate['minimum_candidate_verified_utility_per_hour']
    checks['paired_rate_ratio'] = cr > 0 and ar >= cr * gate['minimum_utility_rate_ratio_each_pair']
    checks['candidate_declared_salvage_policy'] = (
        not any(task['salvaged_tool_prefixes'] for task in candidate['tasks'])
        or candidate_manifest.get('salvage_tool_prefix') is True)
    return checks, {'control_utility_per_hour': cr, 'candidate_utility_per_hour': ar,
                    'ratio': ar / cr if cr > 0 else None}


def assess(control_path, candidate_path):
    summaries = [json.loads((p / 'summary.json').read_text()) for p in (control_path, candidate_path)]
    manifests = [json.loads((p / 'manifest.json').read_text()) for p in (control_path, candidate_path)]
    spec = json.loads((ROOT / 'spec/acceptance.json').read_text())
    checks, rates = pair_checks(*summaries, *manifests, spec)
    audits = [audit(p) for p in (control_path, candidate_path)]
    checks['control_evidence_audit'] = audits[0]['passed']
    checks['candidate_evidence_audit'] = audits[1]['passed']
    checks['distinct_runs'] = control_path.resolve() != candidate_path.resolve() and manifests[0]['run_id'] != manifests[1]['run_id']
    return {'schema_version': 1, 'control_run': str(control_path),
            'candidate_run': str(candidate_path), 'checks': checks, 'rates': rates,
            'pair_metrics_passed': all(checks.values()),
            'candidate_diagnostics': {key: sum(t[key] for t in summaries[1]['tasks'])
                for key in ('model_error_replies', 'rejected_tool_outputs', 'salvaged_tool_prefixes')},
            'summary_sha256': [a['summary_sha256'] for a in audits],
            'scope': 'Necessary metrics for ONE pair only. Two interleaved pairs with the same frozen arms, protocol-test evidence, actual loopback/process observations, permissions and reproduction remain required for promotion.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('control', type=Path)
    parser.add_argument('candidate', type=Path)
    args = parser.parse_args()
    report = assess(args.control.resolve(), args.candidate.resolve())
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['pair_metrics_passed'] else 1)
