#!/usr/bin/env python3
"""AW161 guarded raw-API rollback numeric fidelity diagnostic."""
import fcntl,json,os,subprocess,time
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group
from bonsai_turbo_server import verify,SPEC

def main():
 r=Path('/Users/chad/Models/agentwing/evidence/AW-0161');plan=json.loads((r/'plan.json').read_text())
 assert not (r/'result.json').exists()
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);preflight();verify()
  build=json.loads((ROOT/'evidence/AW-0158-ngram-rollback-build.json').read_text());lib=Path(build['build'])/'bin'
  for n,h in build['artifacts_sha256'].items():assert digest(lib/n)==h
  assert digest(ROOT/'experiments/fixtures/bonsai-rollback-final-case.cpp')==plan['fixture_sha256']
  assert digest(ROOT/'evidence/AW-0158-ngram-rollback-build.json')==plan['build_receipt_sha256']
  prefix=Path('/Users/chad/Models/agentwing/evidence/AW-0148/0-f16/prompt-tokens.bin');ids=Path('/Users/chad/Models/agentwing/evidence/AW-0154/native-ids.bin')
  assert digest(prefix)==plan['prefix_sha256'] and digest(ids)==plan['ids_sha256']
  cmd=[str(r/'fixture'),'/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-attention-PQ2_0.gguf',str(prefix),str(ids),str(r)]
  plan.update(harness_sha256=digest(Path(__file__)),fixture_binary_sha256=digest(r/'fixture'),command=cmd,model_runtime_profile=json.loads(SPEC.read_text()),os=subprocess.check_output(['sw_vers'],text=True),hardware=subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),thermal=subprocess.check_output(['pmset','-g','therm'],text=True),storage='internal SSD',cache='Fresh contexts; uncontrolled OS cache; no speed comparison',watchdog_s=180)
  (r/'execution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
  baseline=host_sample()[1];samples=[];child=None;error=None;start=time.monotonic()
  with (r/'native.log').open('w') as log,(r/'pressure.jsonl').open('w') as pressure:
   try:
    env=os.environ.copy();env.update(plan['env']);check_sample(host_sample(),baseline)
    child=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    while child.poll() is None:
     s=host_sample();samples.append(s);check_sample(s,baseline);pressure.write(json.dumps({'time':time.time(),'pressure':s[0],'swap_mib':s[1]})+'\n');pressure.flush()
     if time.monotonic()-start>180:raise RuntimeError('watchdog')
     time.sleep(.5)
    if child.returncode:raise RuntimeError('fixture-exit-'+str(child.returncode))
   except Exception as exc:error=str(exc)
   finally:stop_group(child)
  result={'experiment':'AW-0161','error':error,'exit':child.returncode if child else None,'baseline_swap_mib':baseline,'pressure_peak':max((s[0] for s in samples),default=None),'swap_growth_peak_mib':max((max(0,s[1]-baseline) for s in samples),default=None),'wall_seconds_diagnostic':time.monotonic()-start,'raw_sha256':{p.name:digest(p) for p in r.iterdir() if p.is_file()},'scope':plan['scope']}
  (r/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result|{'raw_sha256':'saved'}),flush=True)
  if error:raise SystemExit(1)
if __name__=='__main__':main()
