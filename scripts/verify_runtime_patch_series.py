#!/usr/bin/env python3
"""Reconstruct the pinned runtime tree in a temporary Git index."""

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def verify(spec_path):
    spec = json.loads(spec_path.read_text())["swiftlet"]
    repository = Path(spec["local_path"])
    with tempfile.TemporaryDirectory(prefix="agentwing-runtime-index-") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}

        def git(*args):
            return subprocess.check_output(["git", "-C", str(repository), *args],
                                           env=env, text=True).strip()

        git("read-tree", spec["upstream_revision"])
        patches = []
        for entry in spec["patches"]:
            patch = ROOT / entry["path"]
            digest = hashlib.sha256(patch.read_bytes()).hexdigest()
            if digest != entry["sha256"]:
                raise ValueError(f"patch hash mismatch: {entry['path']}")
            git("apply", "--cached", "--whitespace=nowarn", str(patch))
            patches.append({"path": entry["path"], "sha256": digest})
        reconstructed = git("write-tree")
        recorded = git("rev-parse", f"{spec['revision']}^{{tree}}")
        expected = spec.get("source_tree", recorded)
        return {
            "schema_version": 1,
            "upstream_revision": spec["upstream_revision"],
            "runtime_revision": spec["revision"],
            "reconstructed_tree": reconstructed,
            "recorded_commit_tree": recorded,
            "expected_tree": expected,
            "patches": patches,
            "passed": reconstructed == recorded == expected,
            "scope": "Temporary-index source reconstruction; no checkout, build or model execution.",
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=ROOT / "spec/dependencies.json")
    args = parser.parse_args()
    try:
        report = verify(args.spec)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({"passed": False, "error": str(error)}))
        raise SystemExit(1)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
