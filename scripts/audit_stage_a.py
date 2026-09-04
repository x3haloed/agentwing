#!/usr/bin/env python3
"""Audit a completed Stage A run without modifying its retained evidence."""

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

import verify_stage_a as verifier


METRIC = re.compile(
    r"^\[(chatcmpl-[^]]+)\] (\d+) prompt \+ (\d+) reused "
    r"\((\d+) prefix matched\) \+ (\d+) generated, "
    r"ttft ([\d.]+)s, ([\d.]+) tok/s$"
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(run):
    summary = json.loads((run / "summary.json").read_text())
    manifest = verifier.load_manifest()
    expected_ids = [task["id"] for task in manifest["tasks"]]
    recorded_ids = [task["task_id"] for task in summary["tasks"]]
    checks = {
        "completed_full_suite": summary["status"] == "completed"
        and recorded_ids == expected_ids,
    }
    # Resolve archived checksum names inside this run, allowing copied audits.
    for line in (run / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        path = run / Path(name).name
        checks[f"sha256:{path.name}"] = sha256(path) == digest

    requests_seen = set()
    segments = []
    tasks = []
    for result in summary["tasks"]:
        task_id = result["task_id"]
        directory = run / "tasks" / task_id
        transcript = (directory / "pi.jsonl").read_text()
        server_text = (directory / "server.log").read_text()
        lines = server_text.splitlines()
        segments.extend(lines)
        metrics = [match for line in lines if (match := METRIC.match(line))]
        requests = [match[1] for match in metrics]
        events = [json.loads(line) for line in transcript.splitlines()]
        starts, ends, pending = [], [], set()
        paired = True
        for event in events:
            kind = event.get("type")
            if kind == "tool_execution_start":
                key = event["toolCallId"]
                paired &= key not in pending
                pending.add(key)
                starts.append(event)
            elif kind == "tool_execution_end":
                key = event["toolCallId"]
                paired &= key in pending
                pending.discard(key)
                ends.append(event)

        task = verifier.find_task(manifest, task_id)
        # Test commands can create bytecode and other files. Replay on a copy.
        with tempfile.TemporaryDirectory(prefix="agentwing-audit-") as tmp:
            workspace = Path(tmp) / "workspace"
            shutil.copytree(directory / "workspace", workspace)
            failures = verifier.verify(task, workspace)
        source = verifier.SUITE / "tasks" / task_id / "input"
        protected = [path for path in source.rglob("*") if path.is_file()
                     and (path.name.startswith("test_") or path.name == "validate.sh")]
        task_checks = {
            "transcript_hash": sha256(directory / "pi.jsonl") == result["transcript_sha256"],
            # Matching common system tokens is harmless when none were reused.
            "no_cross_task_state_reuse": bool(metrics) and int(metrics[0][3]) == 0,
            "unique_request_ownership": len(requests) == len(set(requests))
            and not requests_seen.intersection(requests),
            "no_foreign_workspace_reference": not any(
                f"/tasks/{other}/workspace" in transcript + server_text
                for other in expected_ids if other != task_id
            ),
            "paired_tool_events": paired and not pending
            and len(starts) == len(ends) == result["tool_calls"],
            "verifier_replay": int(not failures) == result["verifier_utility"],
            "protected_tests_unchanged": all(
                path.read_bytes() == (directory / "workspace" / path.relative_to(source)).read_bytes()
                for path in protected
            ),
            "accepted_utility": result["utility"] == (
                int(not failures) if result["status"] == "completed" else 0
            ),
            "timeout_terminal_boundary": result["status"] != "stopped-timeout"
            or (result["cancellation_drain_observed"] and bool(lines)
                and bool(METRIC.match(lines[-1]))),
        }
        requests_seen.update(requests)
        tasks.append({
            "task_id": task_id,
            "checks": task_checks,
            "request_count": len(metrics),
            "new_prompt_tokens": sum(int(match[2]) for match in metrics),
            "generated_tokens": sum(int(match[5]) for match in metrics),
            "reported_ttft_seconds": round(sum(float(match[6]) for match in metrics), 1),
        })

    server_lines = (run / "server.log").read_text().splitlines()
    checks["task_logs_partition_server_suffix"] = bool(segments) and server_lines[-len(segments):] == segments
    utility = sum(task["utility"] for task in summary["tasks"])
    checks["aggregate_utility"] = summary["utility"] == utility
    checks["aggregate_rate"] = abs(summary["verified_utility_per_hour"] - 3600 * utility / summary["wall_seconds"]) < 1e-9
    samples = [line.split("\t") for line in (run / "pressure.tsv").read_text().splitlines()[1:]]
    pressure_peak = max(int(row[2]) for row in samples)
    swap_peak = max(float(row[3]) for row in samples)
    checks["pressure_gate"] = pressure_peak == summary["pressure_peak"] and pressure_peak < 4
    checks["swap_gate"] = swap_peak == summary["swap_peak_mib"] and swap_peak - summary["swap_used_mib_before"] <= 1024
    return {
        "schema_version": 1,
        "run_id": run.name,
        "summary_sha256": sha256(run / "summary.json"),
        "checks": checks,
        "tasks": tasks,
        "passed": all(checks.values()) and all(all(task["checks"].values()) for task in tasks),
        "scope": "Recorded evidence and copied-workspace replay; not sandbox certification or default promotion.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    report = audit(args.run.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)
