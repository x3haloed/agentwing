#!/usr/bin/env python3
"""Probe native write/network boundaries using disposable canaries only."""

import json
import os
import socket
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="agentwing-boundary-probe-") as raw:
    root = Path(raw).resolve()
    workspace, outside = root / "workspace", root / "outside"
    workspace.mkdir()
    outside.mkdir()
    (workspace / "escape").symlink_to(outside, target_is_directory=True)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(2)
        port = listener.getsockname()[1]
        other_port = port + 1 if port < 65535 else port - 1
        prefix = ["/usr/bin/sandbox-exec", "-f", str(ROOT / "config/task-boundary-probe.sb"),
                  "-D", f"WORKSPACE={workspace}", "-D", f"ENDPOINT=localhost:{port}",
                  "/usr/bin/python3", "-c"]
        cases = {
            "workspace_write": (f"open({str(workspace / 'ok')!r},'w').write('ok')", True),
            "outside_write": (f"open({str(outside / 'bad')!r},'w').write('bad')", False),
            "symlink_escape": (f"open({str(workspace / 'escape' / 'bad')!r},'w').write('bad')", False),
            "permitted_endpoint": (f"import socket; s=socket.socket(); s.connect(('127.0.0.1',{port})); s.close()", True),
            "other_endpoint": (f"import socket; s=socket.socket(); s.connect(('127.0.0.1',{other_port})); s.close()", False),
        }
        results = {}
        for name, (code, allowed) in cases.items():
            result = subprocess.run(prefix + [code], text=True, capture_output=True, timeout=5,
                                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            results[name] = {
                "exit": result.returncode,
                "operation_not_permitted": "Operation not permitted" in result.stderr,
                "expected_outcome": result.returncode == 0 if allowed else
                    result.returncode != 0 and "Operation not permitted" in result.stderr,
            }
    results["canary_integrity"] = {"expected_outcome": (workspace / "ok").read_text() == "ok"
                                   and not list(outside.iterdir())}
    report = {"schema_version": 1, "scope": "Disposable write/network canaries, not a production agent sandbox",
              "results": results, "passed": all(item["expected_outcome"] for item in results.values())}
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
