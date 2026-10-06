#!/usr/bin/env python3
"""AW-0190 diagnostic only: identical saved prefixes, same runtime, two KV formats."""
import fcntl,json,subprocess,time,os
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group
from bonsai_turbo_server import verify,SPEC
R=Path('/Users/chad/Models/agentwing/evidence/AW-0190')
I=Path('/Users/chad/Models/agentwing/evidence/AW-0144')
assert os.access(R/'replay',os.X_OK), 'Replay binary must be executable before freezing'
preflight();verify()
build=json.loads((ROOT/'evidence/AW-0186-stationary-codebook-build.json').read_text())
canary=json.loads((ROOT/'evidence/AW-0189-codebook-metal-attention.json').read_text());assert all(canary['result'][k] for k in ['complete','numeric_passed','quality_gate_passed','cost_gate_passed']) and canary['independent_raw_output_numeric_cost_pipeline_host_replay_valid']
for name,h in build['libraries_sha256'].items():assert digest(Path(build['build_directory'])/'bin'/name)==h
for name,h in build['plan']['changed_sources_sha256'].items():assert digest(Path(build['plan']['source'])/name)==h
for name,h in build['plan']['patch_series_sha256'].items():assert digest(ROOT/name)==h

with (ROOT/'var/model-owner.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 authority=json.loads((ROOT/'evidence/AW-0144-replay-inputs.json').read_text())
 for name,info in authority['inputs'].items():assert digest(I/name)==info['sha256']
 plan={'experiment':'AW-0190','scope':'Early/middle/late stationary-codebook own32 accumulated-cache diagnostic, not endpoint quality/performance','hypothesis':'Stationary same-bit V codec reduces first-row model-logit displacement across accumulated prefixes while preserving finite own trajectories/resource gates','source_sha256':digest(ROOT/'experiments/fixtures/bonsai-stationary-cache-replay.cpp'),'harness_sha256':digest(Path(__file__)),'binary_sha256':digest(R/'replay'),'runtime_spec_sha256':digest(SPEC),'runtime':json.loads(SPEC.read_text()),'headers':{n:digest(Path('/Users/chad/Models/agentwing/runtime-sources/prism-turbo-codebook')/n) for n in ['include/llama.h','ggml/include/ggml.h','ggml/include/ggml-backend.h']},'compiler':subprocess.check_output(['clang++','--version'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internal SSD','cache':'Fresh process per arm; uncontrolled OS page cache; alternating pair order; no speed comparison','inputs':authority['inputs'],'context':16384,'batch':128,'generated_tokens':32,'sampling':{'temperature':1,'top_p':.95,'top_k':20,'min_p':.05,'presence_penalty':0,'repeat_penalty':1,'seed':42},'acceptance':'All arms exit0,32 own sampled tokens/full finite logits; identical prompt-token bytes each pair; first-row identical-prefix full-logit relative L2<=0.10 and top20 overlap>=0.50. Subsequent own-trajectory disagreement descriptive, not equal-prefix numeric comparison. Provisional technical falsifier, not broad quality acceptance. Host pressure<4 and swap growth<=1024MiB; stop on execution failure.','timeout_per_arm_seconds':600,'order':[(n,a) for n,arms in [(0,['f16','turbo']),(4096,['turbo','f16']),(7695,['f16','turbo'])] for a in arms]}
 plan['candidate_build']=build;plan['candidate_canary_sha256']=digest(ROOT/'evidence/AW-0189-codebook-metal-attention.json');plan['candidate_build_receipt_sha256']=digest(ROOT/'evidence/AW-0186-stationary-codebook-build.json');plan['auditor_sha256']=digest(ROOT/'scripts/audit_bonsai_stationary_cache_replay.py')
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 rows=[]
 for position,arm in plan['order']:
  preflight();run=R/f'{position}-{arm}';run.mkdir();baseline=host_sample()[1];samples=[];error=None;start=time.monotonic()
  model=plan['runtime']['model'].get('path') if isinstance(plan['runtime'].get('model'),dict) else None
  if model is None:model=str(Path('/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-attention-PQ2_0.gguf'))
  cmd=[str(R/'replay'),model,str(run),str(I/f'prefix-{position}-chunks.txt'),arm]
  with (run/'capture.tsv').open('w') as out,(run/'native.log').open('w') as err:
   proc=subprocess.Popen(cmd,stdout=out,stderr=err,start_new_session=True)
   try:
    while proc.poll() is None:
     s=host_sample();samples.append(s);check_sample(s,baseline)
     with (run/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
     if time.monotonic()-start>600:raise RuntimeError('timeout')
     time.sleep(.5)
   except Exception as exc:error=str(exc)
   finally:stop_group(proc)
  row={'position_chunks':position,'arm':arm,'baseline_swap_mib':baseline,'exit':proc.returncode,'error':error,'wall_seconds_diagnostic':time.monotonic()-start,'pressure_peak':max(s[0] for s in samples),'swap_growth_peak_mib':max(0,max(s[1] for s in samples)-baseline),'command':cmd,'raw_sha256':{p.name:digest(p) for p in run.iterdir() if p.is_file()}}
  (run/'result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(json.dumps({k:row[k] for k in ['position_chunks','arm','exit','error','wall_seconds_diagnostic']}),flush=True)
  if error or proc.returncode:break
 (R/'execution-summary.json').write_text(json.dumps({'experiment':'AW-0190','rows':rows,'complete':len(rows)==6,'numeric_audit_pending':True},indent=2)+'\n')
 if len(rows)!=6 or any(r['exit'] or r['error'] for r in rows):raise SystemExit(1)
