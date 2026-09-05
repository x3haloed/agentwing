"""AW-0030 standalone probe supervisor; compile native source before running."""
import datetime
import hashlib
import json
from pathlib import Path
import signal
import sys
import subprocess
import time
from run_local_agent import preflight, host_sample, check_sample, stop_group


def main():
    preflight()
    root = Path('/Users/chad/Models/agentwing/evidence/AW-0030')
    run = root / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run.mkdir()
    command = [str(root / 'expert_mapping_v2'), '/Users/chad/Models/agentwing/checkpoints/qwen3.6-35b-a3b-8bit.qpack/packed_experts/layer_00.bin']
    if sys.argv[1:] == ['churn']:
        command.append('churn')
    elif sys.argv[1:]:
        raise SystemExit('usage: probe_expert_mapping.py [churn]')
    baseline = host_sample()[1]
    process = None
    samples = []
    start = time.monotonic()
    error = None
    def interrupt(signum, frame):
        raise KeyboardInterrupt(f'signal-{signum}')
    signal.signal(signal.SIGTERM, interrupt)
    try:
        with (run / 'results.jsonl').open('w') as out, (run / 'stderr.txt').open('w') as err:
            process = subprocess.Popen(command, stdout=out, stderr=err, start_new_session=True)
            while process.poll() is None:
                reading = host_sample()
                samples.append([time.monotonic() - start, *reading])
                check_sample(reading, baseline)
                if time.monotonic() - start > 180:
                    raise RuntimeError('timeout')
                time.sleep(.1)
    except (Exception, KeyboardInterrupt) as exc:
        error = str(exc)
    finally:
        stop_group(process)
    manifest = {'command': command, 'error': error, 'exit': process.returncode if process else None,
                'wall_seconds': time.monotonic() - start, 'pressure_samples': samples,
                'swap_baseline_mib': baseline,
                'os': subprocess.check_output(['sw_vers'], text=True),
                'compiler': subprocess.check_output(['xcrun', 'clang', '--version'], text=True),
                'hashes': {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in
                           ['probes/expert_mapping.m', __file__, command[0]]}}
    (run / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (run / 'probe-source.m').write_bytes(Path('probes/expert_mapping.m').read_bytes())
    print(run)
    print((run / 'stderr.txt').read_text())
    print((run / 'results.jsonl').read_text())
    return 0 if error is None and process.returncode == 0 else 1

if __name__ == '__main__':
    raise SystemExit(main())
