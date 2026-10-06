#!/usr/bin/env python3
"""AW-0143 full-vision16K Turbo server actual medium/xhigh prompt rendering falsifier only."""
import fcntl,json,os,signal,subprocess,time,urllib.request,hashlib
from pathlib import Path
from bonsai_turbo_server import ROOT,command,verify,SPEC
from run_local_agent import preflight,host_sample,check_sample,stop_group
R=Path('/Users/chad/Models/agentwing/evidence/AW-0143')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 preflight();R.mkdir(exist_ok=True)
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);version=verify();baseline=host_sample();cmd=command()+["--verbose"]
  plan={'experiment':'AW-0143','command':cmd,'harness_sha256':sha(__file__),'launcher_sha256':sha(ROOT/'scripts/bonsai_turbo_server.py'),'spec_sha256':sha(SPEC),'version':version,'acceptance':'Actual apply-template default equals explicit medium; xhigh differs with its published instruction; thinking prefix retained; allocator and host gates retained','timeout_seconds':60,'scope':'Actual prompt rendering only; no generation, agent utility or speed claim','os':subprocess.check_output(['sw_vers'],text=True),'host':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internal SSD','cache':'fresh process; uncontrolled OS page cache'}
  assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');samples=[];error=None;ready=False;start=time.monotonic();proc=None;http=[]
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  with (R/'server.log').open('w') as log:
   try:
    proc=subprocess.Popen(cmd,stdout=log,stderr=log,start_new_session=True)
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
    rendered={}
    for mode in ['default','medium','xhigh']:
     body={'messages':[{'role':'user','content':'Explain 17 plus 25.'}],'add_generation_prompt':True}
     if mode!='default':body['reasoning_effort']=mode
     (R/(mode+'-request.json')).write_text(json.dumps(body,indent=2)+'\n')
     req=urllib.request.Request('http://127.0.0.1:8080/apply-template',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
     with opener.open(req,timeout=5) as response:
      raw=response.read();(R/(mode+'-render.json')).write_bytes(raw);rendered[mode]=json.loads(raw)['prompt'];http.append({'endpoint':'apply-template','mode':mode,'status':response.status})
     check_sample(host_sample(),baseline[1])
    render_pass=rendered['default']==rendered['medium'] and rendered['medium']!=rendered['xhigh'] and 'Reasoning effort is set to xhigh.' in rendered['xhigh'] and 'Reasoning effort is set to xhigh.' not in rendered['medium'] and rendered['medium'].endswith('<think>\n')
    if not render_pass:raise RuntimeError('Actual effort rendering mismatch')
    check_sample(host_sample(),baseline[1])
   except Exception as exc:error=str(exc)
   finally:stop_group(proc)
  log=(R/'server.log').read_text();allocation=next((x for x in log.splitlines() if 'K (q8_0):' in x and 'V (turbo4):' in x),'');correct='408.00 MiB' in allocation and '272.00 MiB' in allocation and '136.00 MiB' in allocation
  result={'experiment':'AW-0143','passed':ready and correct and error is None,'rendering_checked':error is None,'error':error,'healthy':ready,'http':http,'allocator_line':allocation,'wall_seconds_diagnostic':time.monotonic()-start,'pressure_peak':max(x[0] for x in samples),'swap_growth_peak_mib':max(0,max(x[1] for x in samples)-baseline[1]),'server_exit_after_cleanup':proc.returncode if proc else None,'plan_sha256':sha(R/'plan.json'),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
