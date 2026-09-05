"""AW-0032: supervised, fixed-route native transport replay."""
import datetime
import hashlib
import json
from pathlib import Path
import signal
import subprocess
import time
from run_local_agent import preflight, host_sample, check_sample, stop_group
from probe_expert_residency import MODEL


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    preflight()
    root = Path('/Users/chad/Models/agentwing/evidence/AW-0032')
    root.mkdir(exist_ok=True)
    run = root / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run.mkdir()
    source = Path('probes/real_route_transport.m')
    trace_root = Path('/Users/chad/Models/agentwing/evidence/AW-0031/20260905T183732Z')
    trace = trace_root / 'T1/experts.jsonl'
    assert sha(trace) == json.loads((trace_root / 'sha256.json').read_text())['T1/experts.jsonl']
    batches = [r for r in map(json.loads, trace.read_text().splitlines()) if r['event'] == 'fetch']
    assert len(batches) == 1000 and sum(len(r['misses']) for r in batches) == 9249
    (run / 'batches.json').write_text(json.dumps(batches) + '\n')
    (run / source.name).write_bytes(source.read_bytes())
    (run / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    binary = run / 'real_route_transport'
    build = ['xcrun', 'clang', '-O2', '-fobjc-arc', '-framework', 'Foundation', '-framework', 'Metal', str(source), '-o', str(binary)]
    with (run / 'build.log').open('w') as log:
        subprocess.run(build, stdout=log, stderr=subprocess.STDOUT, check=True)
    command = [str(binary), MODEL, str(run / 'batches.json')]
    manifest = {'command': command, 'build': build, 'harness_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'trace_sha256': sha(trace), 'binary_sha256': sha(binary), 'source_sha256': sha(source), 'os': subprocess.check_output(['sw_vers'], text=True), 'hardware': subprocess.check_output(['sysctl', 'hw.model', 'hw.memsize', 'hw.ncpu'], text=True), 'storage': subprocess.check_output(['df', '-h', MODEL], text=True), 'thermal_before': subprocess.check_output(['pmset', '-g', 'therm'], text=True), 'compiler': subprocess.check_output(['xcrun', 'clang', '--version'], text=True), 'scope': 'Fixed real misses; GPU scan, no model compute; no cross-batch oracle prefetch; OS cache uncontrolled'}
    (run / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(run, flush=True)
    process = None
    samples = []
    baseline = host_sample()[1]
    start = time.monotonic()
    error = None
    def interrupt(signum, frame):
        raise KeyboardInterrupt(str(signum))
    signal.signal(signal.SIGTERM, interrupt)
    try:
        with (run / 'results.jsonl').open('w') as out, (run / 'stderr.txt').open('w') as err:
            process = subprocess.Popen(command, stdout=out, stderr=err, start_new_session=True)
            while process.poll() is None:
                sample = host_sample()
                samples.append([time.monotonic() - start, *sample])
                check_sample(sample, baseline)
                if time.monotonic() - start > 300:
                    raise RuntimeError('timeout')
                time.sleep(.25)
    except (Exception, KeyboardInterrupt) as exc:
        error = str(exc)
    finally:
        stop_group(process)
    result = {'error': error, 'exit': process.returncode if process else None, 'wall_seconds': time.monotonic() - start, 'pressure_samples': samples, 'swap_baseline_mib': baseline, 'thermal_after': subprocess.check_output(['pmset', '-g', 'therm'], text=True)}
    (run / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    (run / 'sha256.json').write_text(json.dumps({str(p.relative_to(run)): sha(p) for p in run.rglob('*') if p.is_file() and p.name != 'sha256.json'}, indent=2) + '\n')
    print((run / 'results.jsonl').read_text())
    print((run / 'stderr.txt').read_text())
    return 0 if error is None and process.returncode == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
