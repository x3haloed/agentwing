#!/usr/bin/env python3
"""Independent verifier for the frozen Agentwing Stage A suite."""

from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "benchmarks" / "stage-a-v1"
MANIFEST = SUITE / "manifest.json"


def load_manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as handle:
        return json.load(handle)


def verify(task: dict, workspace: Path) -> list[str]:
    failures: list[str] = []
    for check in task["checks"]:
        check_type = check["type"]
        if check_type == "file_exact":
            path = workspace / check["path"]
            actual = path.read_text(encoding="utf-8") if path.is_file() else None
            if actual != check["value"]:
                failures.append(f"{path.name}: exact content mismatch")
        elif check_type == "text_trimmed_exact":
            path = workspace / check["path"]
            actual = path.read_text(encoding="utf-8").strip() if path.is_file() else None
            if actual != check["value"]:
                failures.append(f"{path.name}: trimmed text mismatch")
        elif check_type == "json_exact":
            path = workspace / check["path"]
            try:
                with path.open(encoding="utf-8") as handle:
                    actual = json.load(handle)
            except (FileNotFoundError, json.JSONDecodeError) as error:
                failures.append(f"{path.name}: {error}")
            else:
                if actual != check["value"]:
                    failures.append(f"{path.name}: JSON value mismatch")
        elif check_type == "command":
            result = subprocess.run(
                check["argv"], cwd=workspace, text=True, capture_output=True, timeout=60
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip().splitlines()
                failures.append(
                    f"command {check['argv']!r} exited {result.returncode}: "
                    + (detail[-1] if detail else "no output")
                )
        elif check_type == "source_absent":
            excluded = set(check.get("exclude", []))
            matches = []
            for path in workspace.rglob("*"):
                if (
                    path.is_file()
                    and fnmatch.fnmatch(path.name, check["glob"])
                    and path.name not in excluded
                    and check["value"] in path.read_text(encoding="utf-8")
                ):
                    matches.append(str(path.relative_to(workspace)))
            if matches:
                failures.append(f"forbidden source text remains in {matches}")
        else:
            failures.append(f"unknown check type: {check_type}")
    return failures


def find_task(manifest: dict, task_id: str) -> dict:
    for task in manifest["tasks"]:
        if task["id"] == task_id:
            return task
    raise SystemExit(f"unknown task: {task_id}")


def self_test(manifest: dict) -> int:
    unexpected_passes = []
    for task in manifest["tasks"]:
        with tempfile.TemporaryDirectory(prefix=f"agentwing-{task['id']}-") as tmp:
            workspace = Path(tmp) / "workspace"
            shutil.copytree(SUITE / "tasks" / task["id"] / "input", workspace)
            if not verify(task, workspace):
                unexpected_passes.append(task["id"])
    if unexpected_passes:
        print(f"Stage A self-test: FAIL: pristine tasks passed: {unexpected_passes}")
        return 1
    print(f"Stage A self-test: PASS ({len(manifest['tasks'])} pristine tasks rejected)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task")
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    manifest = load_manifest()
    if args.self_test:
        return self_test(manifest)
    if not args.task or not args.workspace:
        parser.error("--task and --workspace are required unless --self-test is used")
    failures = verify(find_task(manifest, args.task), args.workspace.resolve())
    result = {"task_id": args.task, "utility": 0 if failures else 1, "failures": failures}
    print(json.dumps(result, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
