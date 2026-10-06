#!/usr/bin/env python3
"""AW-0090 native replay of complete AW-0088 prompt activations."""
import fcntl,json,subprocess,time,os,signal,struct,math
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample
r=Path('/Users/chad/Models/agentwing/evidence/AW-0090');capture=Path('/Users/chad/Models/agentwing/evidence/AW-0088');weights=Path('/Users/chad/Models/agentwing/evidence/AW-0086')
preflight()
with (ROOT/'var/model-owner.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 c=json.loads((capture/'result.json').read_text());assert c['passed']
 for n,info in c['capture_files'].items():assert digest(capture/n)==info['sha256']
 w=json.loads((ROOT/'evidence/AW-0086-real-projection-audit.json').read_text())
 for rec in w['records']:
  for n in ['ptq.bin','pq.bin']:assert digest(weights/rec['tensor']/n)==rec['files'][n]
 plan={'experiment':'AW-0090','relative_l2_limit':1e-4,'limit_scope':'Cheap component falsifier, not full-model behavioral acceptance','captured_result_sha256':digest(capture/'result.json'),'weights_receipt_sha256':digest(ROOT/'evidence/AW-0086-real-projection-audit.json'),'native_source_sha256':digest(ROOT/'experiments/fixtures/bonsai-activation-replay-metal.cpp'),'script_sha256':digest(Path(__file__)),'native_binary_sha256':digest(r/'activation-replay'),'columns':1,'input_selection':'First prompt-token column; real input but not generated-token activation','selection':[rec['tensor'] for rec in w['records']],'timeout_seconds_per_projection':90,'comparison':'All native replay outputs against captured full-model PTQ projection output; both PTQ and exact PQ paths','scope':'Single-column native matvec on real prompt-token input; no generated-token capture, candidate accumulation, vision, timing or endpoint claim'}
 assert not (r/'plan.json').exists();(r/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 baseline=host_sample()[1];samples=[];records=[];error=None
 try:
  for i,rec in enumerate(w['records']):
   case=r/rec['tensor'];case.mkdir();width,rows=rec['dimensions'];(case/'input.bin').write_bytes((capture/f'{i}-0.bin').read_bytes()[:width*4]);command=[str(r/'activation-replay'),str(weights/rec['tensor']/'ptq.bin'),str(weights/rec['tensor']/'pq.bin'),str(case/'input.bin'),str(case/'outputs.bin'),str(width),str(rows),'1']
   with (case/'native.log').open('w') as err:
    proc=subprocess.Popen(command,stderr=err,stdout=err,start_new_session=True);start=time.monotonic()
    try:
     while proc.poll() is None:
      s=host_sample();samples.append(s);check_sample(s,baseline)
      with (r/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
      if time.monotonic()-start>90:raise RuntimeError('timeout')
      time.sleep(.25)
    finally:
     if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   assert proc.returncode==0
   raw=(case/'outputs.bin').read_bytes();n=rows;assert len(raw)==n*8
   a=struct.unpack('<'+str(n*2)+'f',raw);expected=struct.unpack('<'+str(n)+'f',(capture/f'{i}-1.bin').read_bytes()[:n*4]);norm=math.fsum(v*v for v in expected)
   metrics={}
   for label,values in [('ptq',a[:n]),('pq',a[n:])]:
    assert all(math.isfinite(v) for v in values)
    relative=math.sqrt(math.fsum((x-y)**2 for x,y in zip(values,expected))/max(norm,1e-30));assert relative<=plan['relative_l2_limit'],f'{rec["tensor"]}:{label}:{relative}'
    metrics[label]={'relative_l2':relative,'max_absolute':max(abs(x-y) for x,y in zip(values,expected))}
   rotated=expected[1:]+expected[:1];negative=math.sqrt(math.fsum((x-y)**2 for x,y in zip(a[:n],rotated))/max(norm,1e-30));assert negative>plan['relative_l2_limit']
   records.append({'tensor':rec['tensor'],'metrics':metrics,'output_values_per_arm':n,'rotated_row_reference_relative_l2':negative,'files':{p.name:digest(p) for p in case.iterdir()}})
 except Exception as exc:error=str(exc) or type(exc).__name__
 result={'experiment':'AW-0090','passed':len(records)==3 and error is None,'error':error,'records':records,'plan_sha256':digest(r/'plan.json'),'pressure_peak':max(s[0] for s in samples),'swap_growth_peak_mib':max(0,max(s[1] for s in samples)-baseline),'pressure_sha256':digest(r/'pressure.tsv'),'external_evidence':str(r),'scope':plan['scope']}
 (r/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
