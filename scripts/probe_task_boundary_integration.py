#!/usr/bin/env python3
"""Disposable inherited-permission checks for the optional task wrapper."""
import json
import socket
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHILD = r'''
import errno, json, os, socket, subprocess, sys
from pathlib import Path
workspace, outside = map(Path, sys.argv[1:3])
allowed_port, denied_port = map(int, sys.argv[3:5])
results = {}

def allowed(name, operation):
    try: operation(); results[name] = True
    except OSError: results[name] = False

def denied(name, operation):
    try: operation(); results[name] = False
    except OSError as error: results[name] = error.errno == errno.EPERM

def write(path): path.write_text('owned canary')
def connect(port):
    with socket.socket() as client: client.connect(('127.0.0.1', port))

allowed('workspace_write', lambda: write(workspace / 'allowed'))
allowed('private_tmp_write', lambda: write(Path(os.environ['TMPDIR']) / 'allowed'))
allowed('dev_null_write', lambda: write(Path('/dev/null')))
denied('outside_write', lambda: write(outside / 'denied'))
denied('symlink_escape', lambda: write(workspace / 'escape' / 'denied'))
allowed('owned_endpoint', lambda: connect(allowed_port))
denied('other_listening_endpoint', lambda: connect(denied_port))
child = subprocess.run([sys.executable, '-c',
    "from pathlib import Path; import sys; Path(sys.argv[1]).write_text('child allowed'); Path(sys.argv[2]).write_text('child denied')",
    str(workspace / 'child-allowed'), str(outside / 'child-denied')], capture_output=True, text=True)
results['child_inherits_boundary'] = (child.returncode != 0
    and 'Operation not permitted' in child.stderr
    and (workspace / 'child-allowed').read_text() == 'child allowed')
print(json.dumps(results))
'''


def main():
    with tempfile.TemporaryDirectory(prefix='agentwing-inherited-boundary-') as raw:
        root = Path(raw).resolve()
        workspace, outside = root / 'workspace', root / 'outside'
        workspace.mkdir()
        outside.mkdir()
        (workspace / 'escape').symlink_to(outside, target_is_directory=True)
        with socket.socket() as allowed_listener, socket.socket() as denied_listener:
            for listener in (allowed_listener, denied_listener):
                listener.bind(('127.0.0.1', 0))
                listener.listen(2)
            allowed_port, denied_port = (s.getsockname()[1] for s in (allowed_listener, denied_listener))
            result = subprocess.run([
                '/usr/bin/python3', str(ROOT / 'scripts/run_task_boundary.py'),
                '--workspace', str(workspace), '--port', str(allowed_port), '--',
                '/usr/bin/python3', '-c', CHILD, str(workspace), str(outside),
                str(allowed_port), str(denied_port)], text=True, capture_output=True, timeout=15)
        checks = json.loads(result.stdout) if result.returncode == 0 else {}
        checks['wrapper_exit'] = result.returncode == 0
        checks['outside_canaries_absent'] = not list(outside.iterdir())
        checks['workspace_canary_present'] = (workspace / 'allowed').exists()
        report = {'schema_version': 1, 'checks': checks,
                  'passed': len(checks) == 11 and all(checks.values()),
                  'stderr': result.stderr,
                  'scope': 'Disposable write/outbound-network and descendant-process probes; no model inference, real Pi protocol, or comprehensive sandbox certification.'}
        print(json.dumps(report, indent=2))
        return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
