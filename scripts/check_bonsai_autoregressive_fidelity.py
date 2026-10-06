#!/usr/bin/env python3
"""AW-0098 bounded interleaved autoregressive fidelity; not endpoint scoring."""
import array,fcntl,hashlib,json,math,os,signal,subprocess,time
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0098')
def streamhash(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def compare(a,b):
 x=a.read_bytes();y=b.read_bytes();assert len(x)==len(y) and len(x)%4==0
 if x==y:return 0.0
 u=array.array('f');u.frombytes(x);v=array.array('f');v.frombytes(y);assert all(math.isfinite(t) for t in u) and all(math.isfinite(t) for t in v)
 return math.sqrt(math.fsum((i-j)**2 for i,j in zip(u,v))/max(math.fsum(i*i for i in u),1e-30))
def main():
 preflight()
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  manifest=json.loads((ROOT/'spec/bonsai-selective-packing-artifact.json').read_text());candidate=Path(manifest['path']);base=candidate.with_name('Ternary-Bonsai-2-27B-PTQ1_0.gguf');assert streamhash(base)=='53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318cfe33ee3' if False else True
  assert streamhash(base)=='53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3';assert streamhash(candidate)==manifest['sha256']
  prompt='Explain why an iterator should not mutate its input list while traversing it.';models={'A':base,'B':candidate}
  libraries={p.name:digest(p) for p in (ROOT/'var/bonsai-demo/bin/mac').glob('*.dylib')}
  plan={'experiment':'AW-0098','order':['A','B','B','A'],'source_sha256':digest(ROOT/'experiments/fixtures/bonsai-autoregressive-activation.cpp'),'script_sha256':digest(Path(__file__)),'binary_sha256':digest(R/'autoregressive-activation'),'artifact_manifest_sha256':digest(ROOT/'spec/bonsai-selective-packing-artifact.json'),'libraries':libraries,'runtime_commit':manifest['runtime_commit'],'base_model_sha256':'53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3','candidate_sha256':manifest['sha256'],'prompt':prompt,'context':2048,'batch':128,'kv':'FP16','reasoning':'Raw text probe, no chat template or reasoning-effort claim; endpoint modes unchanged','sampling':{'temperature':1,'top_k':20,'top_p':.95,'min_p':.05,'presence_penalty':0,'frequency_penalty':0,'repetition_penalty':1,'seed':42},'max_generated_tokens':32,'min_generated_tokens':8,'selected_activation_cap_per_arm_bytes':67108864,'logits_cap_per_arm':'At most32 complete vocab rows','timeout_seconds_per_arm':180,'acceptance':{'token_ids_identical':True,'activation_relative_l2_max':1e-3,'logits_relative_l2_max':1e-3,'finite':True},'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'cache':'Uncontrolled warm OS page/shader cache, fresh model/context per arm','scope':'Bounded candidate-generated dense-model activations/logits on one raw prompt; no vision, protocol, heldout capability, performance or endpoint claim'}
  assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');baseline=host_sample()[1];samples=[];runs=[];comparisons=[];error=None
  try:
   for i,arm in enumerate(plan['order']):
    case=R/f'{i}-{arm}';case.mkdir();start=time.monotonic()
    with (case/'capture.tsv').open('w') as out,(case/'native.log').open('w') as err:
     proc=subprocess.Popen([str(R/'autoregressive-activation'),str(models[arm]),str(case),prompt],stdout=out,stderr=err,start_new_session=True)
     try:
      while proc.poll() is None:
       s=host_sample();samples.append(s);check_sample(s,baseline)
       with (R/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
       if time.monotonic()-start>180:raise RuntimeError('timeout')
       time.sleep(.25)
     finally:
      if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
    wall=time.monotonic()-start;tokens=[int(line.split('\t')[2]) for line in (case/'capture.tsv').read_text().splitlines() if line.startswith('TOKEN\t')]
    runs.append({'arm':arm,'directory':str(case),'exit':proc.returncode,'wall_seconds':wall,'tokens':tokens,'files':{p.name:streamhash(p) for p in case.iterdir()}});assert proc.returncode==0 and len(tokens)>=8
   for left,right in [(0,1),(3,2)]:
    a=Path(runs[left]['directory']);b=Path(runs[right]['directory']);assert runs[left]['tokens']==runs[right]['tokens'];names=sorted(p.name for p in a.glob('*-*.bin'));assert names==sorted(p.name for p in b.glob('*-*.bin'))
    metrics={name:compare(a/name,b/name) for name in names};logits=compare(a/'logits.bin',b/'logits.bin');maximum=max(metrics.values());assert maximum<=1e-3 and logits<=1e-3
    comparisons.append({'control_run':left,'candidate_run':right,'captured_tensor_files':len(names),'maximum_activation_relative_l2':maximum,'logits_relative_l2':logits,'identical_token_count':len(runs[left]['tokens'])})
   for n,h in libraries.items():assert digest(ROOT/'var/bonsai-demo/bin/mac'/n)==h
  except Exception as exc:error=str(exc) or type(exc).__name__
  finally:
   result={'experiment':'AW-0098','passed':len(comparisons)==2 and error is None,'error':error,'runs':[{k:v for k,v in run.items() if k!='files'} for run in runs],'comparisons':comparisons,'plan_sha256':digest(R/'plan.json'),'pressure_peak':max(s[0] for s in samples),'swap_growth_peak_mib':max(0,max(s[1] for s in samples)-baseline),'external_evidence':str(R),'scope':plan['scope']}
   (R/'run-hashes.json').write_text(json.dumps(runs,indent=2)+'\n');(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
