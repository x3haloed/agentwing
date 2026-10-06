#!/usr/bin/env python3
"""AW-0198 full saved request diagnostic; never execute proposed tools."""
import argparse,fcntl,json,os,shutil,subprocess,sys,time,urllib.request
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group,ready
from bonsai_stationary_server import command,verify,SPEC
R=Path('/Users/chad/Models/agentwing/evidence/AW-0198')

INITIAL_FREE_BYTES=16*1024**3
MINIMUM_FREE_BYTES=8*1024**3

def disk_sample(directory, minimum=MINIMUM_FREE_BYTES):
 free=shutil.disk_usage(directory).free
 if free<minimum:raise RuntimeError(f'disk-capacity-gate: free={free}, minimum={minimum}')
 return free

def worker(directory):
 body=json.loads((directory/'request.json').read_text())
 req=urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));terminal=[];done=False;events=0
 with opener.open(req,timeout=1800) as response,(directory/'response.sse').open('wb') as raw:
  for line in response:
   raw.write(line);raw.flush()
   if not line.startswith(b'data: '):continue
   value=line[6:].strip()
   if value==b'[DONE]':done=True;continue
   x=json.loads(value);events+=1
   if 'error' in x:raise RuntimeError(str(x['error']))
   for choice in x.get('choices',[]):
    if choice.get('finish_reason') is not None:terminal.append(choice['finish_reason'])
 result={'http_status':200,'events':events,'done':done,'finish_reasons':terminal,'tools_executed':0}
 (directory/'response-summary.json').write_text(json.dumps(result,indent=2)+'\n')
 if not done or len(terminal)!=1:raise RuntimeError('Nonterminal or ambiguous response')

def main():
 admission=ROOT/'evidence/AW-0192-stationary-admission.json'
 assert admission.exists() and json.loads(admission.read_text())['passed'], 'AW-0192 independent functional admission required'
 disk_sample(R.parent,INITIAL_FREE_BYTES);preflight();version=verify();R.mkdir(exist_ok=True)
 source=Path('/Users/chad/Models/agentwing/evidence/AW-0195/fourth-request.json')
 receipt=json.loads((ROOT/'evidence/AW-0195-stationary-request-comparison.json').read_text());assert digest(source)==receipt['raw_sha256']['fourth-request.json']
 body={'model':'bonsai2-27b','max_tokens':8192,'stream':True,'temperature':1.0,'top_p':.95,'top_k':20,'min_p':.05,'presence_penalty':0,'repeat_penalty':1,'frequency_penalty':0,'seed':42,**json.loads(source.read_text())}
 body.pop('add_generation_prompt',None)
 plan={'experiment':'AW-0198','scope':'Unreplicated full accumulated request behavior, no tools executed or task score/performance claim','source_request_sha256':digest(source),'harness_sha256':digest(Path(__file__)),'runtime_spec_sha256':digest(SPEC),'runtime':json.loads(SPEC.read_text()),'version':version,'request':body,'strict_stream_auditor_sha256':digest(ROOT/'scripts/audit_bonsai_rollback_full_request.py'),'functional_admission_sha256':digest(admission),'history_receipt_sha256':digest(ROOT/'evidence/AW-0195-stationary-request-comparison.json'),'harness_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'disk_policy':{'initial_minimum_free_bytes':INITIAL_FREE_BYTES,'runtime_minimum_free_bytes':MINIMUM_FREE_BYTES,'sample_period_seconds':.5,'stop_remaining_arms_on_capacity_failure':True},'prior_interruption_sha256':digest(ROOT/'evidence/AW-0196-storage-interruption.json'),'failed_combined_screen_sha256':digest(ROOT/'evidence/AW-0197-capacity-current-history-terminal.json'),'order':['q8-f16','f16-turbo'],'startup_timeout_seconds':60,'request_timeout_seconds':1800,'context_tokens':16384,'acceptance':'Fresh clean server; identical request bytes, complete SSE terminal/[DONE] or preserved watchdog failure; all generated tool calls retained but not executed. Host pressure<4/swap growth<=1024MiB. No task success or promotion acceptance.','os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internal SSD','cache':'Fresh server per arm; uncontrolled OS page cache; single fixed Q8-K/F16-V then F16-K/Turbo4-V diagnostic pair, no comparative speed attribution'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 rows=[];selection_error=None
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for arm in plan['order']:
   try:disk_sample(R,INITIAL_FREE_BYTES)
   except RuntimeError as exc:selection_error=str(exc);break
   preflight();directory=R/arm;directory.mkdir();(directory/'request.json').write_text(json.dumps(body,indent=2)+'\n')
   cmd=command()+['--verbose']
   types={'q8-f16':('q8_0','f16'),'f16-turbo':('f16','turbo4')}[arm]
   for flag,value in zip(['--cache-type-k','--cache-type-v'],types):cmd[cmd.index(flag)+1]=value
   (directory/'server-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
   baseline=host_sample()[1];samples=[];free_samples=[];server=client=None;error=None;start=time.monotonic()
   with (directory/'server.log').open('w') as log,(directory/'client.log').open('w') as client_log:
    try:
     server=subprocess.Popen(cmd,stdout=log,stderr=log,start_new_session=True)
     deadline=time.monotonic()+60
     while not ready():
      s=host_sample();samples.append(s);check_sample(s,baseline)
      free=disk_sample(directory);free_samples.append(free)
      with (directory/'capacity.jsonl').open('a') as f:f.write(json.dumps({'time':time.time(),'free_bytes':free})+'\n')
      if server.poll() is not None or time.monotonic()>deadline:raise RuntimeError('startup failed')
      time.sleep(.5)
     client=subprocess.Popen([sys.executable,__file__,'--worker',str(directory)],stdout=client_log,stderr=client_log,start_new_session=True);deadline=time.monotonic()+1800
     while client.poll() is None:
      s=host_sample();samples.append(s);check_sample(s,baseline)
      free=disk_sample(directory);free_samples.append(free)
      with (directory/'capacity.jsonl').open('a') as f:f.write(json.dumps({'time':time.time(),'free_bytes':free})+'\n')
      with (directory/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
      if server.poll() is not None:raise RuntimeError('server exited')
      if time.monotonic()>deadline:raise RuntimeError('request-timeout')
      time.sleep(.5)
     if client.returncode:raise RuntimeError('request worker failed')
    except Exception as exc:error=str(exc)
    finally:stop_group(client);stop_group(server)
   row={'arm':arm,'error':error,'client_exit':client.returncode if client else None,'server_exit_after_cleanup':server.returncode if server else None,'wall_seconds_diagnostic':time.monotonic()-start,'minimum_sampled_free_bytes':min(free_samples,default=None),'baseline_swap_mib':baseline,'pressure_peak':max((s[0] for s in samples),default=None),'swap_growth_peak_mib':max((max(0,s[1]-baseline) for s in samples),default=None),'raw_sha256':{p.name:digest(p) for p in directory.iterdir() if p.is_file()}}
   (directory/'result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(json.dumps(row|{'raw_sha256':'saved'}),flush=True)
   if error and error.startswith('disk-capacity-gate:'):break
 (R/'summary.json').write_text(json.dumps({'experiment':'AW-0198','rows':rows,'selection_error':selection_error,'unattempted':plan['order'][len(rows):],'tools_executed':0,'scope':plan['scope']},indent=2)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--worker',type=Path);args=p.parse_args()
 if args.worker:worker(args.worker)
 else:main()
