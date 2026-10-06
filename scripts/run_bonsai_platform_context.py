#!/usr/bin/env python3
"""AW212 shared macOS-context Pi-only matched cache falsifier, no endpoint score."""
import datetime,fcntl,json,shutil,subprocess,sys,time,urllib.request
from pathlib import Path
from bonsai_turbo6_server import ROOT,command,verify,SPEC
from run_local_agent import preflight,digest,host_sample,check_sample,stop_group
R=Path('/Users/chad/Models/agentwing/evidence/AW-0212')
def main():
 preflight();verify();R.mkdir(exist_ok=False)
 source=Path('/Users/chad/Models/agentwing/evidence/AW-0211/20261006T204724Z-rep1/pi-workspace/source.txt');fixture=R/'source-fixture.txt';fixture.write_bytes(source.read_bytes())
 pins=['scripts/run_bonsai_platform_context.py','scripts/probe_bonsai_platform_pi.py','scripts/bonsai_turbo6_server.py','scripts/bonsai_turbo_server.py','scripts/bonsai_server.py','scripts/run_task_boundary.py','scripts/run_local_agent.py','scripts/run_bonsai_budget_debugging_v2.py','spec/bonsai-turbo6-local.json','config/pi-bonsai-turbo-models.json','config/task-boundary.sb','node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js']
 plan={'experiment':'AW-0212','hypothesis':'Shared explicitmacOS/Darwin utility context allows allfourPi exact-copy/zero-execution-error runs with F16 and6bit caches','acceptance':'All4Pi exit0, byteexactsamefixtureartifact, no model/protocol/permission/executionfailure, pressure<4/swapgrowth<=1024MiB/disk16GiBstartup8GiBruntime; manualtoolclassification required; anyfailure stops remainingarms','order':['f16','turbo6','turbo6','f16'],'scope':'Pi-only platform-context functional falsifier with fullvisionserverloaded; no image-understandingrerun or fullmultimodal/endpoint/causalprompt/speed claim','pins':{n:digest(ROOT/n) for n in pins},'configuration':json.loads(SPEC.read_text()),'parent_receipt_sha256':digest(ROOT/'evidence/AW-0211-turbo6-admission-terminal.json'),'source_fixture_sha256':digest(fixture),'prompt_revision':'Added only: Host platform: macOS (Darwin). Shell utilities are the macOS versions. Same task/tools/permissions/reasoning/sampling/caps/scoring, no commandbans orrepairshims. Collector now enforces existing zero-error audit gate.','harness':'Pi0.84.4','startup_timeout_seconds':180,'arm_timeout_seconds':1800,'pi_child_timeout_seconds':900,'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.run(['pmset','-g','therm'],text=True,capture_output=True).stdout,'storage':'internalSSD, freshservers, OS cacheuncontrolled','setup_note':'artifactverification precedes monitoredarms, no completeendpointoverheadclaim'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');rows=[]
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for i,arm in enumerate(plan['order']):
   preflight();assert shutil.disk_usage(R).free>=16*1024**3;run=R/f'{i}-{arm}';run.mkdir();cmd=command()+['--verbose']
   if arm=='f16':
    for flag in ['--cache-type-k','--cache-type-v']:cmd[cmd.index(flag)+1]='f16'
   (run/'command.json').write_text(json.dumps(cmd,indent=2)+'\n');baseline=host_sample()[1];server=client=None;error=None;start=time.monotonic()
   with (run/'server.log').open('w') as log,(run/'client.log').open('w') as cl,(run/'pressure.jsonl').open('w') as trace:
    def sample():
     s=host_sample();free=shutil.disk_usage(R).free;trace.write(json.dumps({'time':time.time(),'pressure':s[0],'swap_mib':s[1],'free_bytes':free})+'\n');trace.flush();check_sample(s,baseline);assert free>=8*1024**3
    try:
     server=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);deadline=time.monotonic()+180;ready=False
     while not ready:
      sample();assert server.poll() is None
      try:
       with urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=1) as response:ready=response.status==200
      except OSError:pass
      if time.monotonic()>deadline:raise RuntimeError('startuptimeout')
      time.sleep(1)
     client=subprocess.Popen([sys.executable,str(ROOT/'scripts/probe_bonsai_platform_pi.py'),str(run),'--source-fixture',str(fixture)],stdout=cl,stderr=subprocess.STDOUT,start_new_session=True)
     while client.poll() is None:
      sample();assert server.poll() is None
      if time.monotonic()-start>1800:raise RuntimeError('armtimeout')
      time.sleep(1)
     if client.returncode:raise RuntimeError('Pi fixtureexit '+str(client.returncode))
    except Exception as exc:error=str(exc)
    finally:stop_group(client);stop_group(server)
   report={'index':i,'arm':arm,'passed':error is None,'error':error,'baseline_swap_mib':baseline,'client_exit':client.returncode if client else None,'server_exit_after_cleanup':server.returncode if server else None,'wall_seconds_diagnostic':time.monotonic()-start};(run/'result.json').write_text(json.dumps(report,indent=2)+'\n');(run/'sha256.json').write_text(json.dumps({p.name:digest(p) for p in run.iterdir() if p.is_file()},indent=2)+'\n');rows.append(report);print(json.dumps(report),flush=True)
   if error:break
 (R/'execution-summary.json').write_text(json.dumps({'experiment':'AW-0212','complete':len(rows)==4,'rows':rows,'unattempted':plan['order'][len(rows):]},indent=2)+'\n')
if __name__=='__main__':main()
