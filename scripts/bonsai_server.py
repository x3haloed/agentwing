#!/usr/bin/env python3
"""Serve the pinned local Bonsai multimodal configuration with a host watchdog."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from run_local_agent import host_sample, check_sample, stop_group

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'spec/bonsai-local.json'
WEIGHTS = Path('/Users/chad/Models/agentwing/checkpoints/bonsai2-27b')
BINARY = ROOT / 'var/bonsai-demo/bin/mac/llama-server'


def command(port=8080):
    s = json.loads(SPEC.read_text())
    model, projector = [WEIGHTS / a['filename'] for a in s['model']['artifacts']]
    return [str(BINARY), '--model', str(model), '--mmproj', str(projector),
            '--alias', 'bonsai2-27b', '--host', '127.0.0.1', '--port', str(port),
            '--ctx-size', str(s['context_tokens']), '--parallel', '1', '-ngl', '99',
            '--batch-size', '256', '--ubatch-size', '128', '--image-max-tokens', str(s['image_max_tokens']),
            '--jinja', '--reasoning-effort', s['reasoning_effort'], '--temp', '1.0',
            '--top-p', '0.95', '--top-k', '20', '--min-p', '0.05', '--repeat-penalty', '1.0', '--seed', '42']


def verify():
    s = json.loads(SPEC.read_text())
    for a in s['model']['artifacts']:
        p = WEIGHTS / a['filename']
        if p.stat().st_size != a['bytes']:
            raise RuntimeError(f'Artifact size mismatch: {p}')
        h = hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
                h.update(b)
        if h.hexdigest() != a['sha256']:
            raise RuntimeError(f'Artifact hash mismatch: {p}')
    expected = s['runtime'].get('server_sha256')
    if expected and hashlib.sha256(BINARY.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Server binary hash mismatch')
    version = subprocess.check_output([str(BINARY), '--version'], stderr=subprocess.STDOUT, text=True)
    if 'adfffbe41' not in version:
        raise RuntimeError(f'Wrong runtime: {version}')
    return version.strip()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', type=int, default=8080)
    p.add_argument('--verify-only', action='store_true')
    args = p.parse_args()
    if not 1 <= args.port <= 65535:
        p.error('Invalid port')
    lockpath=ROOT/'var/model-owner.lock'
    lockpath.parent.mkdir(exist_ok=True)
    lock=lockpath.open('w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    print(verify(), flush=True)
    if args.verify_only:
        return
    found = subprocess.run(['pgrep', '-f', 'llama-server|swiftlet-server|mlx_lm.server|ollama runner|TurboFieldfare'], capture_output=True, text=True)
    if found.returncode == 0:
        raise RuntimeError('Another model-owning process is running; stop it first')
    run = Path('/Users/chad/Models/agentwing/evidence/AW-0062') / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ-server')
    run.mkdir(parents=True)
    cmd = command(args.port)
    (run / 'command.json').write_text(json.dumps(cmd, indent=2)+'\n')
    baseline = host_sample()[1]
    child = None
    try:
        check_sample(host_sample(), baseline)
        with (run / 'server.log').open('w') as log, (run / 'pressure.jsonl').open('w') as pressure:
            child = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            print(f'Bonsai local endpoint: http://127.0.0.1:{args.port}; evidence: {run}', flush=True)
            while child.poll() is None:
                sample = host_sample()
                pressure.write(json.dumps({'time':time.time(),'pressure':sample[0],'swap_mib':sample[1]})+'\n'); pressure.flush()
                check_sample(sample, baseline)
                time.sleep(1)
            if child.returncode:
                raise RuntimeError(f'Server exited {child.returncode}; inspect {run}/server.log')
    finally:
        stop_group(child)


if __name__ == '__main__':
    main()
