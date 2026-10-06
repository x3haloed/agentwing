#!/usr/bin/env python3
"""AW-0151 full-vision16K Turbo server history speculation startup/resource falsifier only."""
import fcntl,json,os,signal,subprocess,time,urllib.request,hashlib
from pathlib import Path
from bonsai_turbo_server import ROOT,command,verify,SPEC
from run_local_agent import preflight,host_sample,check_sample,stop_group
R=Path('/Users/chad/Models/agentwing/evidence/AW-0151')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 preflight();R.mkdir(exist_ok=True)
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);version=verify();baseline=host_sample();cmd=command()+["--verbose","--spec-type","ngram-simple","--spec-ngram-simple-size-n","4","--spec-ngram-simple-size-m","3"]
  env={**os.environ,"GGML_METAL_PTQ1_MULTICOL":"1"}
  plan={'experiment':'AW-0151','command':cmd,'harness_sha256':sha(__file__),'launcher_sha256':sha(ROOT/'scripts/bonsai_turbo_server.py'),'spec_sha256':sha(SPEC),'version':version,'acceptance':'Full vision16K server healthy within60s, props response readable, explicit q8 K/Turbo4 V/408MiB allocation and host gates; no generation/vision quality acceptance','timeout_seconds':60,'scope':'History speculation+PTQ multicol startup only; no inference fidelity or endpoint performance claim','environment_overrides':{'GGML_METAL_PTQ1_MULTICOL':'1'},'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internal SSD','cache':'Fresh server, uncontrolled OS page cache'}
  assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');samples=[];error=None;ready=False;start=time.monotonic();proc=None;http=[]
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  with (R/'server.log').open('w') as log:
   try:
    proc=subprocess.Popen(cmd,stdout=log,stderr=log,start_new_session=True,env=env)
    while proc.poll() is None and time.monotonic()-start<60:
     s=host_sample();samples.append(s);check_sample(s,baseline[1])
     with (R/'host.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
     try:
      with opener.open('http://127.0.0.1:8080/health',timeout=1) as response:body=response.read();ready=response.status==200
      if ready:
       (R/'health.json').write_bytes(body);http.append({'endpoint':'health','status':200});break
     except Exception:pass
     time.sleep(.25)
    if not ready:raise RuntimeError('server not healthy before startup deadline')
    with opener.open('http://127.0.0.1:8080/props',timeout=5) as response:(R/'props.json').write_bytes(response.read());http.append({'endpoint':'props','status':response.status})
    check_sample(host_sample(),baseline[1])
   except Exception as exc:error=str(exc)
   finally:stop_group(proc)
  log=(R/'server.log').read_text();allocation=next((x for x in log.splitlines() if 'K (q8_0):' in x and 'V (turbo4):' in x),'');correct='408.00 MiB' in allocation and '272.00 MiB' in allocation and '136.00 MiB' in allocation
  result={'experiment':'AW-0151','passed':ready and correct and error is None,'error':error,'healthy':ready,'http':http,'allocator_line':allocation,'wall_seconds_diagnostic':time.monotonic()-start,'pressure_peak':max(x[0] for x in samples),'swap_growth_peak_mib':max(0,max(x[1] for x in samples)-baseline[1]),'server_exit_after_cleanup':proc.returncode if proc else None,'plan_sha256':sha(R/'plan.json'),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
