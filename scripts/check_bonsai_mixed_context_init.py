#!/usr/bin/env python3
"""AW182 guarded full16K F16K/Turbo4V context admission; no generation."""
import fcntl,json,subprocess,time
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group
from bonsai_turbo_server import verify,SPEC
R=Path('/Users/chad/Models/agentwing/evidence/AW-0182')
def main():
 assert not (R/'init-result.json').exists();preflight();verify()
 authority=json.loads((R/'build-result.json').read_text());B=Path(authority['build_directory'])/'bin'
 for name,h in authority['libraries_sha256'].items():assert digest(B/name)==h
 command=[str(R/'context-init'),'/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-attention-PQ2_0.gguf',str(R),'/Users/chad/Models/agentwing/evidence/AW-0144/prefix-7695-chunks.txt','f16-turbo']
 plan={'experiment':'AW-0182','scope':'Context initialization/graph reservation/allocator admission only; no tokens decoded, sampling, tools or vision encoded','source_sha256':digest(ROOT/'experiments/fixtures/bonsai-mixed-context-init.cpp'),'runner_sha256':digest(Path(__file__)),'binary_sha256':digest(R/'context-init'),'build_result_sha256':digest(R/'build-result.json'),'model_profile':json.loads(SPEC.read_text()),'command':command,'acceptance':'Exit0 and CONTEXT_INIT_OK; native16K allocator Kf16/Vturbo4; pressure<4/swapgrowth<=1024MiB;90s watchdog','os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internalSSD','cache':'Fresh process; warmed uncontrolled OS page cache'}
 (R/'init-plan.json').write_text(json.dumps(plan,indent=2)+'\n');samples=[];baseline=host_sample()[1];error=None;proc=None;start=time.monotonic()
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);preflight()
  with (R/'init.log').open('w') as log:
   try:
    proc=subprocess.Popen(command,stdout=log,stderr=log,start_new_session=True)
    while proc.poll() is None:
     s=host_sample();samples.append(s);check_sample(s,baseline)
     with (R/'init-pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
     if time.monotonic()-start>90:raise RuntimeError('timeout')
     time.sleep(.25)
   except Exception as exc:error=str(exc)
   finally:stop_group(proc)
 log=(R/'init.log').read_text();allocation=next((l for l in log.splitlines() if '16384 cells' in l and 'K (' in l),'');passed=proc is not None and proc.returncode==0 and error is None and 'CONTEXT_INIT_OK' in log and 'K (f16):' in allocation and 'V (turbo4):' in allocation
 result={'experiment':'AW-0182','passed':passed,'exit':proc.returncode if proc else None,'error':error,'allocator':allocation,'wall_seconds_diagnostic':time.monotonic()-start,'pressure_peak':max((s[0] for s in samples),default=None),'baseline_swap_mib':baseline,'swap_growth_peak_mib':max((max(0,s[1]-baseline) for s in samples),default=None),'plan_sha256':digest(R/'init-plan.json'),'raw_sha256':{n:digest(R/n) for n in ['init.log','init-pressure.tsv']},'scope':plan['scope']};(R/'init-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 if not passed:raise SystemExit(1)
if __name__=='__main__':main()
