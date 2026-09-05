"""Regression cases for accidental promotion from insufficient evidence."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from assess_stage_a_pair import pair_checks


class PairGateTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT / 'spec/acceptance.json').read_text())
        ids = [t['id'] for t in json.loads((ROOT / 'benchmarks/stage-a-v1/manifest.json').read_text())['tasks']]
        self.control = {'utility': 3, 'wall_seconds': 5400, 'status': 'completed',
                        'pressure_peak': 1, 'swap_peak_mib': 100, 'swap_used_mib_before': 100,
                        'tasks': [{'task_id': i, 'model_error_replies': 0,
                                   'rejected_tool_outputs': 0, 'salvaged_tool_prefixes': 0} for i in ids]}
        self.candidate = copy.deepcopy(self.control)
        self.candidate.update(utility=4, wall_seconds=3000)
        self.manifest = dict(task_selection='all', bind='127.0.0.1', suite_id='fixed',
                             suite_sha256='fixed', task_timeout_seconds=900, tools=['bash'],
                             storage='internal-ssd', os_version='fixed', os_build='fixed')

    def checks(self):
        return pair_checks(self.control, self.candidate, self.manifest,
                           self.manifest, self.spec)[0]

    def test_valid_metrics_and_reject_partial_fast_run(self):
        self.assertTrue(all(self.checks().values()))
        self.candidate['tasks'].pop()
        self.assertFalse(self.checks()['candidate_full_suite'])

    def test_ratio_does_not_replace_success_count(self):
        self.candidate.update(utility=2, wall_seconds=500)
        self.assertTrue(self.checks()['paired_rate_ratio'])
        self.assertFalse(self.checks()['minimum_candidate_successes'])
        self.assertFalse(self.checks()['preserved_control_successes'])

    def test_historical_floor_and_host_gates(self):
        self.control['wall_seconds'] = 20000
        self.candidate.update(utility=3, wall_seconds=4000)
        self.assertTrue(self.checks()['paired_rate_ratio'])
        self.assertFalse(self.checks()['historical_floor_rate'])
        self.candidate['pressure_peak'] = 4
        self.candidate['swap_peak_mib'] = 1125
        self.assertFalse(self.checks()['candidate_pressure'])
        self.assertFalse(self.checks()['candidate_swap'])
        before = self.checks()
        self.candidate['tasks'][0]['model_error_replies'] = 1
        self.candidate['tasks'][0]['rejected_tool_outputs'] = 1
        self.assertEqual(self.checks(), before)

    def test_salvage_must_be_declared_but_is_not_automatically_failure(self):
        self.candidate['tasks'][0]['salvaged_tool_prefixes'] = 1
        self.assertFalse(self.checks()['candidate_declared_salvage_policy'])
        self.manifest['salvage_tool_prefix'] = True
        self.assertTrue(all(self.checks().values()))

    def test_different_permission_policy_cannot_form_a_pair(self):
        candidate_manifest = {**self.manifest, 'permission_policy': 'scoped'}
        checks, _ = pair_checks(self.control, self.candidate, self.manifest,
                               candidate_manifest, self.spec)
        self.assertFalse(checks['same_recorded_permissions'])
