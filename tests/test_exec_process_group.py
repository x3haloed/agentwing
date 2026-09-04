#!/usr/bin/env python3
"""Verify task timeouts terminate descendants, not only their wrapper."""

from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "exec_process_group.py"


class ProcessGroupTests(unittest.TestCase):
    def test_helper_changes_directory_before_exec(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["/usr/bin/python3", str(HELPER), "--cwd", tmp, "--", "/bin/pwd"],
                text=True,
                capture_output=True,
                timeout=5,
                check=True,
            )
            self.assertEqual(Path(result.stdout.strip()).resolve(), Path(tmp).resolve())

    def test_group_signal_terminates_shell_and_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            child_pid_file = Path(tmp) / "child.pid"
            process = subprocess.Popen(
                [
                    "/usr/bin/python3",
                    str(HELPER),
                    "/bin/sh",
                    "-c",
                    f"sleep 60 & echo $! > {child_pid_file}; wait",
                ]
            )
            for _ in range(100):
                if child_pid_file.is_file():
                    break
                time.sleep(0.01)
            self.assertTrue(child_pid_file.is_file())
            child_pid = int(child_pid_file.read_text(encoding="utf-8"))
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
            for _ in range(100):
                try:
                    os.kill(child_pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.01)
            else:
                self.fail("child survived process-group termination")


if __name__ == "__main__":
    unittest.main()
