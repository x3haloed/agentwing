"""AW-0031 bounded isolated inference trace and observer-overhead bracket."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from run_local_agent import preflight, host_sample, check_sample, stop_group
from probe_expert_residency import PROMPT, MODEL


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    preflight()
    root=Path('/Users/chad/Models/agentwing/evidence/AW-0031')
    source=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0031')
    binary=source/'.build/release/swiftlet'
    run=root/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run.mkdir()
    files=['Sources/SwiftletCore/ExpertIOTrace.swift','Sources/SwiftletCore/ExpertCache.swift','Sources/SwiftletCore/QwenMetalModel.swift']
    manifest={'prompt':PROMPT,'model':MODEL,'runtime_base':'459b2011375022a6716463bd1e1f1b00741f91c3','binary_sha256':sha(binary),'sampler_sha256':sha(root/'process_io_trace'),'source_sha256':{f:sha(source/f) for f in files},'script_sha256':sha(__file__),'cache_gb':.5,'max_new':24,'order':['C1','T1','C2'],'scope':'Actual inference; observer diagnostic, not agent performance trial','os':subprocess.check_output(['sw_vers'],text=True)}
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for f in files:(run/Path(f).name).write_bytes((source/f).read_bytes())
    print(run,flush=True);results=[]
    def interrupt(signum,frame):raise KeyboardInterrupt(str(signum))
    signal.signal(signal.SIGTERM,interrupt)
    for arm in manifest['order']:
        outdir=run/arm;outdir.mkdir();process=sampler=None;error=None;readings=[];baseline=host_sample()[1];start=time.monotonic()
        env={k:v for k,v in os.environ.items() if k!='SWIFTLET_EXPERT_TRACE'}
        if arm=='T1':env['SWIFTLET_EXPERT_TRACE']=str(outdir/'experts.jsonl')
        cmd=[str(binary),'generate',MODEL,'--gpu','--cache-gb','0.5','--prompt',PROMPT,'--max-new','24']
        try:
            with (outdir/'stdout.txt').open('w') as out,(outdir/'stderr.txt').open('w') as err,(outdir/'io.jsonl').open('w') as io:
                process=subprocess.Popen(cmd,stdout=out,stderr=err,start_new_session=True,env=env)
                sampler=subprocess.Popen([str(root/'process_io_trace'),str(process.pid)],stdout=io,stderr=subprocess.DEVNULL,start_new_session=True)
                while process.poll() is None:
                    sample=host_sample();readings.append([time.monotonic()-start,*sample]);check_sample(sample,baseline)
                    if time.monotonic()-start>180:raise RuntimeError('timeout')
                    time.sleep(.25)
        except (Exception,KeyboardInterrupt) as exc:error=str(exc)
        finally:
            stop_group(process);stop_group(sampler)
        row={'arm':arm,'exit':process.returncode if process else None,'error':error,'wall_seconds':time.monotonic()-start,'swap_baseline_mib':baseline,'pressure_samples':readings}
        (outdir/'result.json').write_text(json.dumps(row,indent=2)+'\n');results.append(row)
        print(json.dumps({k:v for k,v in row.items() if k!='pressure_samples'}),flush=True)
        if error is not None or process.returncode!=0:break
    (run/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    (run/'sha256.json').write_text(json.dumps({str(f.relative_to(run)):sha(f) for f in run.rglob('*') if f.is_file() and f.name!='sha256.json'},indent=2)+'\n')
    return 0 if len(results)==3 and all(r['exit']==0 and r['error'] is None for r in results) else 1

if __name__=='__main__':raise SystemExit(main())
