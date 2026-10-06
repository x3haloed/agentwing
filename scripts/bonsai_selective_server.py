#!/usr/bin/env python3
"""Experimental selective Bonsai full vision launcher, not a promoted profile."""
import argparse,datetime,fcntl,json,subprocess,time
from pathlib import Path
import bonsai_server as base
from run_local_agent import host_sample,check_sample,stop_group
ROOT=base.ROOT
SPEC=ROOT/'spec/bonsai-selective-local.json'
base.SPEC=SPEC
verify=base.verify

def command(port=8080):
    return base.command(port)+['--ctx-checkpoints','2','--cache-ram','0','--no-context-shift','--presence-penalty','0','--frequency-penalty','0']

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
    run = Path('/Users/chad/Models/agentwing/evidence/AW-0099') / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ-server')
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
