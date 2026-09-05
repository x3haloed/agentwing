#!/usr/bin/env python3
"""Run the validated local agent on a preserved copy of a workspace."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RUNS = Path('/Users/chad/Models/agentwing/tasks')
MODEL_PROCESSES = 'swiftlet-server|swiftlet generate|TurboFieldfare|mlx_lm.server|llama-server|ollama runner'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def host_sample():
    pressure = int(subprocess.check_output(['/usr/sbin/sysctl', '-n', 'kern.memorystatus_vm_pressure_level'], text=True))
    swap = subprocess.check_output(['/usr/sbin/sysctl', '-n', 'vm.swapusage'], text=True)
    match = re.search(r'used\s*=\s*([\d.]+)M', swap)
    if pressure <= 0 or not match:
        raise RuntimeError('Host pressure/swap reading unavailable')
    return pressure, float(match[1])


def check_sample(sample, baseline):
    pressure, swap = sample
    if pressure >= 4:
        raise RuntimeError('stopped-critical-pressure')
    if swap - baseline > 1024:
        raise RuntimeError('stopped-swap-growth')


def stop_group(process):
    if process is None:
        return
    process.poll()  # Reap an exited parent before signaling its former group.
    members = subprocess.run(['/usr/bin/pgrep', '-g', str(process.pid)], capture_output=True)
    if members.returncode == 1:
        process.wait(timeout=5)
        return
    if members.returncode != 0:
        raise RuntimeError('Cannot inspect owned process group')
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    # The parent may have exited while a descendant still owns the group.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=5)


def supervise(client, server, baseline, sample, emit, timeout=900, interval=1):
    started = time.monotonic()
    while True:
        reading = sample()
        emit(reading)
        check_sample(reading, baseline)
        result = client.poll()
        if result is not None:
            return result
        if server.poll() is not None:
            raise RuntimeError('server-exited')
        if time.monotonic() - started >= timeout:
            raise RuntimeError('stopped-timeout')
        time.sleep(interval)


def ready():
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open('http://127.0.0.1:8080/v1/models', timeout=1) as response:
            return response.status == 200
    except OSError:
        return False


def pi_command(workspace, models, task):
    spec = json.loads((ROOT / 'spec/validated-local-agent.json').read_text())
    return ['/usr/bin/python3', str(ROOT / 'scripts/run_task_boundary.py'),
            '--workspace', str(workspace), '--models-file', str(models), '--port', '8080', '--',
            spec['environment']['AGENTWING_NODE_BIN'],
            str(ROOT / 'node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js'),
            '--provider', 'agentwing-swiftlet', '--model', 'qwen3.6-35b-a3b-8bit-qpack',
            '--mode', 'json', '--print', '--no-session', '--approve', '--offline', '--tools', 'bash',
            '--system-prompt', (ROOT / 'config/validated-local-agent-prompt.txt').read_text().rstrip('\n'), task]


def execute(run, server_command, client_command, timeout=900, sample=host_sample):
    """Own both sessions; preserve evidence even on interruption or host stop."""
    server = client = None
    baseline = sample()[1]
    started = time.monotonic()
    readings = []
    status, error, client_exit = 'failed', None, None
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    def emit(reading):
        readings.append(reading)
        with (run / 'pressure.tsv').open('a') as handle:
            handle.write(f'{datetime.datetime.now(datetime.timezone.utc).isoformat()}\t{reading[0]}\t{reading[1]}\n')
    try:
        check_sample(sample(), baseline)
        with (run / 'server.log').open('w') as server_log, (run / 'pi.jsonl').open('w') as pi_log, (run / 'pi.stderr').open('w') as pi_err:
            server = subprocess.Popen(server_command, stdout=server_log, stderr=subprocess.STDOUT, start_new_session=True, env=env)
            deadline = time.monotonic() + 60
            while not ready():
                reading = sample(); emit(reading); check_sample(reading, baseline)
                if server.poll() is not None:
                    raise RuntimeError('server-exited-during-startup')
                if time.monotonic() >= deadline:
                    raise RuntimeError('server-startup-timeout')
                time.sleep(0.5)
            client = subprocess.Popen(client_command, stdout=pi_log, stderr=pi_err, start_new_session=True, env=env)
            client_exit = supervise(client, server, baseline, sample, emit, timeout)
            status = 'client-completed' if client_exit == 0 else 'client-failed'
        if status == 'client-completed':
            events = [json.loads(line) for line in (run / 'pi.jsonl').read_text().splitlines() if line.strip()]
            if not events or any(e.get('type') == 'message_end' and e.get('message', {}).get('stopReason') == 'error' for e in events):
                status = 'model-error-or-empty-transcript'
    except (Exception, KeyboardInterrupt) as exc:
        error = str(exc) or type(exc).__name__
    finally:
        stop_group(client)
        stop_group(server)
        report = {'status': status, 'error': error, 'pi_exit': client_exit,
                  'wall_seconds': time.monotonic() - started, 'verified_utility': None,
                  'scope': 'User task, not scored benchmark. Inspect artifacts and independently validate.',
                  'pressure_peak': max((p for p, _ in readings), default=None),
                  'swap_growth_peak_mib': max((s - baseline for _, s in readings), default=None),
                  'server_pid': server.pid if server else None, 'client_pid': client.pid if client else None}
        (run / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
        hashes = {p.name: digest(p) for p in run.iterdir() if p.is_file() and p.name != 'sha256.json'}
        (run / 'sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    return report


def preflight():
    subprocess.run(['/usr/bin/python3', str(ROOT / 'scripts/run_frozen_arm.py'),
                    str(ROOT / 'evidence/AW-0027-frozen-plan-v2.json'), 'A2', '--check-only'],
                   check=True, stdout=subprocess.DEVNULL)
    settings = json.loads((ROOT / 'spec/validated-local-agent.json').read_text())['settings']
    for path, key in [('config/pi-models-validated.json', 'pi_models_sha256'),
                      ('config/validated-local-agent-prompt.txt', 'system_prompt_sha256')]:
        if digest(ROOT / path) != settings[key]:
            raise RuntimeError(f'Validated input changed: {path}')
    check_sample(host_sample(), host_sample()[1])
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 8080))
    result = subprocess.run(['/usr/bin/pgrep', '-f', MODEL_PROCESSES], capture_output=True)
    if result.returncode != 1:
        raise RuntimeError('Another model owner exists or process check failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path)
    parser.add_argument('--task-file', type=Path)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    (ROOT / 'var').mkdir(exist_ok=True)
    with (ROOT / 'var/local-agent.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        preflight()
        if args.check_only:
            print('Validated inputs, host readings, model ownership and port: PASS')
            return 0
        if not args.workspace or not args.task_file:
            parser.error('--workspace and --task-file are required')
        source = args.workspace.resolve(strict=True)
        task = args.task_file.read_text()
        if not source.is_dir() or source == source.parent or not task.strip():
            parser.error('A non-root workspace and non-empty task are required')
        if source == RUNS or source in RUNS.parents:
            parser.error('Workspace must not contain the task evidence directory')
        size = 0
        for folder, _, names in os.walk(source, followlinks=False):
            for name in names:
                path = Path(folder) / name
                if not path.is_symlink():
                    if not path.is_file():
                        parser.error('Workspace contains a special file')
                    size += path.stat().st_size
        RUNS.mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(RUNS).free < size + 1024**3:
            raise RuntimeError('Insufficient free space for workspace copy plus 1GiB reserve')
        run = RUNS / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        run.mkdir(mode=0o700)
        shutil.copytree(source, run / 'workspace', symlinks=True)
        (run / 'task.txt').write_text(task)
        shutil.copyfile(ROOT / 'config/pi-models-validated.json', run / 'pi-models.json')
        shutil.copyfile(ROOT / 'config/validated-local-agent-prompt.txt', run / 'system-prompt.txt')
        deps = json.loads((ROOT / 'spec/dependencies.json').read_text())
        server = [str(Path(deps['swiftlet']['local_path']) / '.build/release/swiftlet-server'),
                  '--model', deps['qwen3_6_35b_a3b_8bit_qpack']['local_path'], '--port', '8080',
                  '--cache-gb', '0.5', '--debug-tool-output', '--accept-schema-tags',
                  '--salvage-tool-prefix', '--allow-repeated-ngrams', '--stop-after-tool-call']
        manifest = {'source_workspace': str(source), 'profile': json.loads((ROOT / 'spec/validated-local-agent.json').read_text()),
                    'launcher_sha256': digest(__file__), 'server_command': server,
                    'free_bytes_before': shutil.disk_usage(RUNS).free}
        (run / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(f'run_dir={run}', flush=True)
        def interrupted(signum, frame):
            raise KeyboardInterrupt(f'signal-{signum}')
        signal.signal(signal.SIGTERM, interrupted)
        report = execute(run, server, pi_command(run / 'workspace', run / 'pi-models.json', task))
        print(json.dumps(report, indent=2))
        return 0 if report['status'] == 'client-completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
