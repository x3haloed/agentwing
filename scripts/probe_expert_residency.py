"""AW-0029 bounded diagnostic using existing Swiftlet counters; no runtime edits."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from run_local_agent import ROOT, preflight, host_sample, check_sample, stop_group

SWIFT = Path('/Users/chad/Models/agentwing/dependencies/Swiftlet')
MODEL = '/Users/chad/Models/agentwing/checkpoints/qwen3.6-35b-a3b-8bit.qpack'
PROMPT = 'Write a Python function that returns the first duplicate item in a list, or None if there are no duplicates.\n\ndef first_duplicate(items):\n'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    preflight()
    run = Path('/Users/chad/Models/agentwing/evidence/AW-0029') / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run.mkdir(parents=True)
    binary = SWIFT / '.build/release/swiftlet'
    manifest = {'prompt': PROMPT, 'arms': [['C1', .5], ['A1', .75], ['C2', .5]],
                'max_new': 24, 'binary_sha256': sha(binary),
                'runtime_revision': subprocess.check_output(['git', '-C', str(SWIFT), 'rev-parse', 'HEAD'], text=True).strip(),
                'agentwing_revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                'model': MODEL, 'model_revision': json.loads((ROOT/'spec/dependencies.json').read_text())['qwen3_6_35b_a3b_8bit_qpack']['revision'],
                'os': subprocess.check_output(['sw_vers'], text=True), 'scope':'CLI component diagnostic, not agent benchmark',
                'script_sha256':sha(__file__)}
    (run/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'run_dir={run}', flush=True)
    results=[]
    for arm, cache in manifest['arms']:
        directory=run/arm;directory.mkdir();baseline=host_sample()[1];p=None;status='failed';start=time.monotonic();samples=[];error=None
        command=[str(binary),'generate',MODEL,'--prompt',PROMPT,'--max-new','24','--gpu','--cache-gb',str(cache)]
        try:
            check_sample(host_sample(),baseline)
            with (directory/'stdout.txt').open('w') as out,(directory/'stderr.txt').open('w') as err:
                p=subprocess.Popen(command,stdout=out,stderr=err,start_new_session=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
                while p.poll() is None:
                    reading=host_sample();samples.append([time.monotonic()-start,*reading]);check_sample(reading,baseline)
                    if time.monotonic()-start>180:raise RuntimeError('timeout')
                    time.sleep(1)
                status='completed' if p.returncode==0 else 'process-failed'
        except (Exception,KeyboardInterrupt) as exc:error=str(exc) or type(exc).__name__
        finally:stop_group(p)
        row={'arm':arm,'cache_gb':cache,'status':status,'error':error,'exit':p.returncode if p else None,'wall_seconds':time.monotonic()-start,
             'pressure_peak':max((x[1] for x in samples),default=None),'swap_growth_peak_mib':max((x[2]-baseline for x in samples),default=None),'command':command}
        (directory/'pressure.json').write_text(json.dumps(samples)+'\n');(directory/'result.json').write_text(json.dumps(row,indent=2)+'\n');results.append(row);print(json.dumps(row),flush=True)
        if status!='completed':break
    (run/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    (run/'sha256.json').write_text(json.dumps({str(p.relative_to(run)):sha(p) for p in run.rglob('*') if p.is_file() and p.name!='sha256.json'},indent=2)+'\n')
    return 0 if len(results)==3 and all(x['status']=='completed' for x in results) else 1

if __name__=='__main__':raise SystemExit(main())
