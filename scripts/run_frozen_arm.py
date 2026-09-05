#!/usr/bin/env python3
"""Verify an immutable comparison plan, then run one full-suite arm."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('slot', choices=['C1', 'A1', 'C2', 'A2'])
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    for name, expected in plan['file_hashes'].items():
        actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f'Frozen input changed: {name}')
    env = {k: v for k, v in os.environ.items() if not k.startswith('AGENTWING_')}
    env.update(plan['common_environment'])
    env.update(plan['arms'][args.slot[0]])
    print(json.dumps({'slot': args.slot, 'plan_sha256': hashlib.sha256(args.plan.read_bytes()).hexdigest(),
                      'environment': {k: v for k, v in env.items() if k.startswith('AGENTWING_')}}, indent=2), flush=True)
    if not args.check_only:
        os.chdir(plan['repository'])
        os.execve('/bin/sh', ['/bin/sh', str(Path(plan['repository']) / 'scripts/run-aw-0008.sh'), '--all'], env)


if __name__ == '__main__':
    main()
