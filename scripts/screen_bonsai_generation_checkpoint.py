#!/usr/bin/env python3
"""AW222 cheap restored-prefix distribution falsifier, not qualification."""
import concurrent.futures,fcntl,hashlib,json,math,os,shutil,subprocess,time,urllib.request
from pathlib import Path
from bonsai_turbo6_server import command,verify,ROOT
from run_local_agent import preflight,host_sample,check_sample,stop_group
R=Path('/Users/chad/Models/agentwing/evidence/AW-0222/cheap-restore')
B=Path('/Users/chad/Models/agentwing/runtime-builds/prism-gen-checkpoints/bin/llama-server')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def http(path,body):
 req=urllib.request.Request('http://127.0.0.1:8080'+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=300) as f:return json.load(f)
def main():
 preflight();assert not R.exists();assert shutil.disk_usage(R.parent).free>=16*1024**3
 pins=json.loads((ROOT/'evidence/AW-0222-isolated-build.json').read_text())
 for name,h in pins['artifacts_sha256'].items():assert digest(B.parent/name)==h
 verify();R.mkdir(mode=0o700)
 cmd=command();cmd[0]=str(B);cmd+=['--verbose']
 plan={'experiment':'AW-0222','stage':'cheap distribution falsifier only','command':cmd,'env':{'AGENTWING_GENERATION_CHECKPOINTS':'1'},'fixture':'Continue the sequence of integers, separated by spaces: 1 2 3 4 5','generation_tokens':640,'replay_prefix_generated_tokens':550,'tolerance_max_top32_logprob_difference':0.01,'acceptance':'checkpoint restored beyond initial prompt; same next token and top32 IDs; finite logprob difference<=0.01; resource gates. Passing does not satisfy full-logit/cost/endpoint gates.','sampling':'diagnostic greedy only; no agent sampling change','runner_sha256':digest(Path(__file__)),'build_receipt_sha256':digest(ROOT/'evidence/AW-0222-isolated-build.json'),'os':subprocess.check_output(['sw_vers'],text=True),'thermal':subprocess.run(['pmset','-g','therm'],capture_output=True,text=True).stdout,'storage':'internalSSD, freshprocess, OS cache uncontrolled'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');baseline=host_sample()[1];start=time.monotonic();proc=None;error=None;result={}
 def sample():
  if proc and proc.poll() is not None:raise RuntimeError('server-exited')
  p,s=host_sample();check_sample((p,s),baseline);free=shutil.disk_usage(R).free
  with (R/'host.jsonl').open('a') as f:f.write(json.dumps({'time':time.time(),'pressure':p,'swap_mib':s,'free_bytes':free})+'\n')
  if free<8*1024**3:raise RuntimeError('disk-gate')
  if time.monotonic()-start>600:raise RuntimeError('phase-timeout')
 def request(name,path,body):
  (R/(name+'-request.json')).write_text(json.dumps(body)+'\n');begin=time.monotonic()
  with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
   future=pool.submit(http,path,body)
   while not future.done():sample();time.sleep(.5)
   response=future.result()
  (R/(name+'-response.json')).write_text(json.dumps(response)+'\n')
  return response,time.monotonic()-begin
 with (ROOT/'var/model-owner.lock').open('a') as lock,(R/'server.log').open('w') as log:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  proc=subprocess.Popen(cmd,stdout=log,stderr=log,start_new_session=True,env={**os.environ,**plan['env']})
  try:
   ready=time.monotonic()+60
   while True:
    sample()
    try:
     with urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=1) as f:assert json.load(f)['status']=='ok'
     break
    except Exception:
     if time.monotonic()>ready:raise RuntimeError('startup-timeout')
     time.sleep(.5)
   tokenized,_=request('tokenize','/tokenize',{'content':plan['fixture'],'add_special':True})
   tokens=tokenized['tokens'];common={'temperature':0,'seed':42,'ignore_eos':True,'return_tokens':True,'stream':False,'top_k':20,'top_p':.95,'min_p':.05,'repeat_penalty':1,'presence_penalty':0}
   generation,gwall=request('generate','/completion',{**common,'prompt':tokens,'n_predict':640,'cache_prompt':True})
   assert len(generation['tokens'])==640,'short-generation'
   prompt=tokens+generation['tokens'][:550]
   replay={**common,'prompt':prompt,'n_predict':1,'n_probs':32,'post_sampling_probs':False}
   restored,rwall=request('restored','/completion',{**replay,'cache_prompt':True})
   fresh,fwall=request('fresh','/completion',{**replay,'cache_prompt':False})
   result={'generated_tokens':len(generation['tokens']),'generation_wall':gwall,'restored_wall':rwall,'fresh_wall':fwall,'restored_tokens':restored['tokens'],'fresh_tokens':fresh['tokens'],'numeric_audit_pending':True}
  except Exception as exc:error=str(exc)
  finally:stop_group(proc)
 result.update({'error':error,'server_exit':proc.returncode,'wall_seconds':time.monotonic()-start,'scope':plan['stage']})
 (R/'result.json').write_text(json.dumps(result,indent=2)+'\n');(R/'hashes.json').write_text(json.dumps({p.name:digest(p) for p in R.iterdir() if p.is_file()},indent=2)+'\n');print(json.dumps(result))
 if error:raise SystemExit(1)
if __name__=='__main__':main()
