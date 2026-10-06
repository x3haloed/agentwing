#!/usr/bin/env python3
"""Measure full text/vision server allocations without scoring a task."""
import datetime
import fcntl
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from bonsai_server import ROOT, command, verify
from run_local_agent import preflight, host_sample, check_sample, stop_group, digest


def main():
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        preflight(); verify()
        run=Path('/Users/chad/Models/agentwing/evidence/AW-0073')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        run.mkdir(parents=True, mode=0o700)
        cmd=command()
        cmd[cmd.index('--ctx-size')+1]='16384'
        cmd+=['--ctx-checkpoints','2','--cache-ram','0','--log-verbosity','5','--presence-penalty','0','--frequency-penalty','0','--no-context-shift']
        manifest={'scope':'Startup allocation diagnostic only; no performance/capability claim',
                  'command':cmd,'source_sha256':digest(__file__),'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),
                  'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internal SSD',
                  'cache':'existing OS page cache uncontrolled; fresh process',
                  'configuration':json.loads((ROOT/'spec/bonsai-capacity-candidate.json').read_text())}
        (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(run,flush=True)
        server=None; samples=[]; baseline=host_sample()[1]; error=None; ready=False; start=time.monotonic()
        try:
            with (run/'server.log').open('w') as log:
                server=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                ready_at=None
                while time.monotonic()-start<60:
                    pressure,swap=host_sample()
                    rss=subprocess.run(['ps','-o','rss=','-p',str(server.pid)],capture_output=True,text=True).stdout.strip()
                    samples.append({'seconds':time.monotonic()-start,'pressure':pressure,'swap_mib':swap,'rss_kib':int(rss) if rss else None})
                    check_sample((pressure,swap),baseline)
                    if server.poll() is not None:raise RuntimeError(f'server exited {server.returncode}')
                    try:
                        with urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=.3) as response:
                            ready=response.status==200
                    except Exception:pass
                    if ready and ready_at is None:ready_at=time.monotonic()
                    if ready_at and time.monotonic()-ready_at>=3:break
                    time.sleep(.5)
                if not ready:raise RuntimeError('startup timeout')
        except Exception as exc:error=str(exc)
        finally:
            stop_group(server)
            report={'ready':ready,'error':error,'samples':samples,'pressure_peak':max(s['pressure'] for s in samples),
                    'swap_growth_peak_mib':max(s['swap_mib']-baseline for s in samples),
                    'rss_peak_kib':max(s['rss_kib'] or 0 for s in samples),'wall_seconds':time.monotonic()-start}
            (run/'result.json').write_text(json.dumps(report,indent=2)+'\n')
            (run/'sha256.json').write_text(json.dumps({p.name:digest(p) for p in run.iterdir() if p.is_file()},indent=2)+'\n')
        print(json.dumps({k:v for k,v in report.items() if k!='samples'}),flush=True)
        if error:raise SystemExit(1)


if __name__=='__main__':main()
