"""Cancellation boundaries must ignore diagnostic noise and stale metrics."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from wait_terminal_metric import wait_for_terminal


METRIC = "[chatcmpl-ABCD] 480 prompt + 0 reused (0 prefix matched) + 0 generated, ttft 0.0s, 0.00 tok/s\n"


class TerminalMetricTests(unittest.TestCase):
    def test_only_complete_new_metric_is_a_barrier(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "server.log"
            for suffix, expected in [
                ("", False),
                ("[tool-replay] hit calls=1\n", False),
                (METRIC.rstrip("\n"), False),
                (METRIC, True),
                ("[tool-replay] hit calls=1\n" + METRIC, True),
            ]:
                with self.subTest(suffix=suffix):
                    log.write_text(METRIC + suffix)
                    self.assertEqual(wait_for_terminal(log, 1, timeout=0), expected)

    def test_missing_metric_has_bounded_wait(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "server.log"
            log.write_text("unrelated diagnostic\n")
            self.assertFalse(wait_for_terminal(log, 0, timeout=0.01, interval=0.005))
