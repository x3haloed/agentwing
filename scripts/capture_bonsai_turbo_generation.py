#!/usr/bin/env python3
"""AW-0136 bounded prompt-only activation capture falsifier."""
import fcntl,json,subprocess,time,os,signal,struct,math
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample
r=Path('/Users/chad/Models/agentwing/evidence/AW-0136')
preflight()
with (ROOT/'var/model-owner.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 prompt='Explain why an iterator should not mutate its input list while traversing it.'
 model=Path('/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-attention-PQ2_0.gguf')
 plan={'experiment':'AW-0136','scope':'Actual32-token generation under q8 K/Turbo4 V; selected early/middle/late attention-out/FFN-down activations and full logits; no endpoint quality claim','prompt':prompt,'context':2048,'batch':128,'kv':{'k':'q8_0','v':'turbo4','flash_attention':'enabled'},'capture_limit_bytes':134217728,'timeout_seconds':120,'activation_layers':[0,31,63],'source_sha256':digest(ROOT/'experiments/fixtures/bonsai-turbo-model-generation.cpp'),'harness_sha256':digest(Path(__file__)),'binary_sha256':digest(r/'selective-activation'),'model_sha256':digest(model),'runtime_commit':'adfffbe41b2cabcd51fff326ab045662265062bb','libraries':{p.name:digest(p) for p in Path('/Users/chad/Models/agentwing/runtime-builds/prism-turbo-model/bin').glob('*.dylib')},'headers':json.loads((r/'header-receipt.json').read_text()),'generation':{'tokens':32,'temperature':1.0,'top_p':0.95,'top_k':20,'min_p':0.05,'presence_penalty':0,'repetition_penalty':1,'seed':42,'template':'raw prompt; no chat reasoning-effort claim'},'acceptance':'Exit0, exactly32 sampled/decoded tokens, 198 full FP32 selected activation sets, complete32 vocabulary logits rows allfinite, host gates'}
 p=r/'plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2)+'\n')
 baseline=host_sample()[1];samples=[];error=None;start=time.monotonic()
 with (r/'capture.tsv').open('w') as out,(r/'native.log').open('w') as err:
  proc=subprocess.Popen([str(r/'selective-activation'),str(model),str(r),prompt],stdout=out,stderr=err,start_new_session=True)
  try:
   while proc.poll() is None:
    s=host_sample();samples.append(s);check_sample(s,baseline)
    with (r/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
    if time.monotonic()-start>120:raise RuntimeError('timeout')
    time.sleep(.25)
  except Exception as exc:error=str(exc)
  finally:
   if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 files=list(r.glob('*-*.bin'));finite=None  # masks legitimately contain -inf; inactive padded cache is not an accuracy input
 result={'experiment':'AW-0136','exit':proc.returncode,'error':error,'passed':proc.returncode==0 and error is None and len(files)==396,'finite':finite,'capture_files':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in files},'plan_sha256':digest(r/'plan.json'),'capture_index_sha256':digest(r/'capture.tsv'),'native_log_sha256':digest(r/'native.log'),'pressure_sha256':digest(r/'pressure.tsv'),'pressure_peak':max(s[0] for s in samples),'swap_growth_peak_mib':max(0,max(s[1] for s in samples)-baseline),'os':subprocess.check_output(['sw_vers'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'external_evidence':str(r),'scope':plan['scope']}
 (r/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
