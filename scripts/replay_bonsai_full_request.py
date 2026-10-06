#!/usr/bin/env python3
"""AW-0149 full saved request diagnostic; never execute proposed tools."""
import argparse,fcntl,json,os,subprocess,sys,time,urllib.request
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group,ready
from bonsai_turbo_server import command,verify,SPEC
R=Path('/Users/chad/Models/agentwing/evidence/AW-0149')

def worker(directory):
 body=json.loads((directory/'request.json').read_text())
 req=urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));terminal=[];done=False;events=0
 with opener.open(req,timeout=1800) as response,(directory/'response.sse').open('wb') as raw:
  for line in response:
   raw.write(line);raw.flush()
   if not line.startswith(b'data: '):continue
   value=line[6:].strip()
   if value==b'[DONE]':done=True;break
   x=json.loads(value);events+=1
   if 'error' in x:raise RuntimeError(str(x['error']))
   for choice in x.get('choices',[]):
    if choice.get('finish_reason') is not None:terminal.append(choice['finish_reason'])
 result={'http_status':200,'events':events,'done':done,'finish_reasons':terminal,'tools_executed':0}
 (directory/'response-summary.json').write_text(json.dumps(result,indent=2)+'\n')
 if not done or len(terminal)!=1:raise RuntimeError('Nonterminal or ambiguous response')

def main():
 preflight();version=verify();R.mkdir(exist_ok=True)
 source=Path('/Users/chad/Models/agentwing/evidence/AW-0145/fourth-request.json')
 receipt=json.loads((ROOT/'evidence/AW-0145-full-render.json').read_text());assert digest(source)==receipt['raw_sha256']['fourth-request.json']
 body={'model':'bonsai2-27b','max_tokens':8192,'stream':True,'temperature':1.0,'top_p':.95,'top_k':20,'min_p':.05,'presence_penalty':0,'repeat_penalty':1,'frequency_penalty':0,'seed':42,**json.loads(source.read_text())}
 body.pop('add_generation_prompt',None)
 plan={'experiment':'AW-0149','scope':'Unreplicated full accumulated request behavior, no tools executed or task score/performance claim','source_request_sha256':digest(source),'harness_sha256':digest(Path(__file__)),'runtime_spec_sha256':digest(SPEC),'runtime':json.loads(SPEC.read_text()),'version':version,'request':body,'order':['f16','turbo'],'startup_timeout_seconds':60,'request_timeout_seconds':1800,'context_tokens':16384,'acceptance':'Fresh clean server; identical request bytes, complete SSE terminal/[DONE] or preserved watchdog failure; all generated tool calls retained but not executed. Host pressure<4/swap growth<=1024MiB. No task success or promotion acceptance.','os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internal SSD','cache':'Fresh server per arm; uncontrolled OS page cache; single fixed F16/Turbo diagnostic pair, no comparative speed attribution'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 rows=[]
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for arm in plan['order']:
   preflight();directory=R/arm;directory.mkdir();(directory/'request.json').write_text(json.dumps(body,indent=2)+'\n')
   cmd=command()+['--verbose']
   if arm=='f16':
    for flag in ['--cache-type-k','--cache-type-v']:cmd[cmd.index(flag)+1]='f16'
   (directory/'server-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
   baseline=host_sample()[1];samples=[];server=client=None;error=None;start=time.monotonic()
   with (directory/'server.log').open('w') as log,(directory/'client.log').open('w') as client_log:
    try:
     server=subprocess.Popen(cmd,stdout=log,stderr=log,start_new_session=True)
     deadline=time.monotonic()+60
     while not ready():
      s=host_sample();samples.append(s);check_sample(s,baseline)
      if server.poll() is not None or time.monotonic()>deadline:raise RuntimeError('startup failed')
      time.sleep(.5)
     client=subprocess.Popen([sys.executable,__file__,'--worker',str(directory)],stdout=client_log,stderr=client_log,start_new_session=True);deadline=time.monotonic()+1800
     while client.poll() is None:
      s=host_sample();samples.append(s);check_sample(s,baseline)
      with (directory/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
      if server.poll() is not None:raise RuntimeError('server exited')
      if time.monotonic()>deadline:raise RuntimeError('request-timeout')
      time.sleep(.5)
     if client.returncode:raise RuntimeError('request worker failed')
    except Exception as exc:error=str(exc)
    finally:stop_group(client);stop_group(server)
   row={'arm':arm,'error':error,'client_exit':client.returncode if client else None,'server_exit_after_cleanup':server.returncode if server else None,'wall_seconds_diagnostic':time.monotonic()-start,'baseline_swap_mib':baseline,'pressure_peak':max((s[0] for s in samples),default=None),'swap_growth_peak_mib':max((max(0,s[1]-baseline) for s in samples),default=None),'raw_sha256':{p.name:digest(p) for p in directory.iterdir() if p.is_file()}}
   (directory/'result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(json.dumps(row|{'raw_sha256':'saved'}),flush=True)
 (R/'summary.json').write_text(json.dumps({'experiment':'AW-0149','rows':rows,'tools_executed':0,'scope':plan['scope']},indent=2)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--worker',type=Path);args=p.parse_args()
 if args.worker:worker(args.worker)
 else:main()
