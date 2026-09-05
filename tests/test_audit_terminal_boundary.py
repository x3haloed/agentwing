import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_stage_a import has_terminal_boundary


class AuditTerminalBoundaryTests(unittest.TestCase):
    metric = '[chatcmpl-A] 64 prompt + 2007 reused (2007 prefix matched) + 27 generated, ttft 18.4s, 2.36 tok/s'

    def test_metric_and_same_request_post_generation_diagnostics(self):
        for suffix in [[], ['[chatcmpl-A] rejected tool output: "partial call"'],
                       ['[chatcmpl-A] normalized declared schema-property tags',
                        '[chatcmpl-A] salvaged complete tool-call prefix before malformed suffix']]:
            with self.subTest(suffix=suffix):
                self.assertTrue(has_terminal_boundary([self.metric] + suffix))

    def test_missing_metric_foreign_request_and_new_activity_reject(self):
        for lines in [[], ['[chatcmpl-A] rejected tool output: "partial"'],
                      [self.metric, '[chatcmpl-B] rejected tool output: "partial"'],
                      [self.metric, '[tool-replay] hit calls=1'],
                      [self.metric, '[chatcmpl-A] unknown diagnostic']]:
            with self.subTest(lines=lines):
                self.assertFalse(has_terminal_boundary(lines))


if __name__ == '__main__':
    unittest.main()
