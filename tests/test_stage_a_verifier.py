#!/usr/bin/env python3
"""Regression tests for the Stage A benchmark and its independent verifier."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_stage_a  # noqa: E402


class StageAVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = verify_stage_a.load_manifest()

    def workspace(self, task_id: str, root: Path) -> Path:
        source = verify_stage_a.SUITE / "tasks" / task_id / "input"
        destination = root / "workspace"
        shutil.copytree(source, destination)
        return destination

    def test_pristine_tasks_fail(self):
        for task in self.manifest["tasks"]:
            with self.subTest(task=task["id"]), tempfile.TemporaryDirectory() as tmp:
                workspace = self.workspace(task["id"], Path(tmp))
                self.assertTrue(verify_stage_a.verify(task, workspace))

    def test_known_solutions_pass(self):
        solutions = {
            "01-navigation": {"ANSWER.txt": "2750"},
            "02-single-file-fix": {
                "math_utils.py": (
                    "def clamp(value: int, lower: int, upper: int) -> int:\n"
                    "    return max(lower, min(value, upper))\n"
                )
            },
            "03-multi-file-fix": {
                "slug.py": (
                    "from config import NAMESPACE\n\n"
                    "def display_slug(text: str) -> str:\n"
                    "    words = [word for word in text.lower().split() if word]\n"
                    "    return f\"{NAMESPACE}/{'-'.join(words)}\"\n"
                )
            },
            "04-refactor": {
                "totals.py": "def nonnegative_total(values):\n    return sum(v for v in values if v >= 0)\n",
                "alpha.py": "from totals import nonnegative_total\n\ndef alpha_total(values):\n    return nonnegative_total(values)\n",
                "beta.py": "from totals import nonnegative_total\n\ndef beta_total(values):\n    return nonnegative_total(values)\n",
            },
            "05-data-transform": {
                "summary.json": json.dumps(
                    {
                        "total_events": 6,
                        "successful_events": 4,
                        "latency_ms_by_service": {"api": 63, "db": 60, "worker": 27},
                    },
                    separators=(",", ":"),
                )
                + "\n"
            },
            "06-failure-recovery": {
                "app.py": (
                    "def normalize(name: str) -> str:\n"
                    "    return '-'.join(name.strip().lower().split())\n"
                )
            },
            "07-bounded-read": {"ANSWER.txt": "req-0173\n"},
            "08-config-sync": {
                "config.json": (
                    '{"bind":"127.0.0.1","max_tool_result_chars":4096,'
                    '"experiment":"stage-a"}\n'
                )
            },
        }
        for task in self.manifest["tasks"]:
            with self.subTest(task=task["id"]), tempfile.TemporaryDirectory() as tmp:
                workspace = self.workspace(task["id"], Path(tmp))
                for relative, content in solutions[task["id"]].items():
                    (workspace / relative).write_text(content, encoding="utf-8")
                self.assertEqual(verify_stage_a.verify(task, workspace), [])


if __name__ == "__main__":
    unittest.main()
