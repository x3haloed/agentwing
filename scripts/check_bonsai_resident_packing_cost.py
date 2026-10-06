#!/usr/bin/env python3
"""AW-0095 projection cost screen; never endpoint utility evidence."""
import fcntl,json,subprocess,time,os,signal,statistics
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample
r=Path('/Users/chad/Models/agentwing/evidence/AW-0095');w=Path('/Users/chad/Models/agentwing/evidence/AW-0094/weights');c=Path('/Users/chad/Models/agentwing/evidence/AW-0093')
preflight()
with (ROOT/'var/model-owner.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 prior=json.loads(Path('/Users/chad/Models/agentwing/evidence/AW-0094/weights-receipt.json').read_text());cp=json.loads((c/'plan.json').read_text())
 for n,h in cp['libraries'].items():assert digest(ROOT/'var/bonsai-demo/bin/mac'/n)==h
 cases=[]
 for i,rec in enumerate(prior['records']):
  if 'ffn_down' in rec['tensor']:continue
  for n in ['ptq.bin','pq.bin']:assert digest(w/rec['tensor']/n)==rec['files'][n]
  cases.extend({'tensor':rec['tensor'],'capture_index':i,'dimensions':rec['dimensions'],'columns':columns} for columns in [1,16])
 plan={'experiment':'AW-0095','cases':cases,'order':'ABBA repeated 3 times per case; first ABBA warmup retained but excluded from steady diagnostic','metrics':['installation_ms','compute_ms','readback_cleanup_ms','graph_total_ms','process_wall_seconds'],'rule':'Retain attention-only packing for full working-set screen only if warm compute PTQ/PQ >1 at every tested single-column layer; no promotion','timeout_seconds':90,'source_sha256':digest(ROOT/'experiments/fixtures/bonsai-resident-packing-cost.cpp'),'script_sha256':digest(Path(__file__)),'binary_sha256':digest(r/'packing-cost'),'libraries':cp['libraries'],'weights_receipt_sha256':digest(Path('/Users/chad/Models/agentwing/evidence/AW-0094/weights-receipt.json')),'capture_receipt_sha256':digest(c/'result.json'),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),'thermal_before':subprocess.check_output(['pmset','-g','therm'],text=True),'resident_policy':'Both arm weights and inputs installed once, two graphs retained across trials; setup logged separately','cache':'OS page/shader cache uncontrolled; source files warm; fresh Metal backend per case','scope':'Resident attention-output graph cost; both arms coexist, repeated fixed real prompt input, no full working-set or endpoint claim'}
 assert not (r/'plan.json').exists();(r/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');baseline=host_sample()[1];samples=[];records=[];error=None
 try:
  for case in cases:
   dest=r/(case['tensor']+'-'+str(case['columns']));dest.mkdir();width,rows=case['dimensions'];inputpath=c/f'{case["capture_index"]}-0.bin';assert digest(inputpath)==json.loads((c/'result.json').read_text())['capture_files'][inputpath.name]['sha256']
   cmd=[str(r/'packing-cost'),str(w/case['tensor']/'ptq.bin'),str(w/case['tensor']/'pq.bin'),str(inputpath),str(width),str(rows),str(case['columns'])]
   with (dest/'timings.tsv').open('w') as out,(dest/'native.log').open('w') as err:
    start=time.monotonic();proc=subprocess.Popen(cmd,stdout=out,stderr=err,start_new_session=True)
    try:
     while proc.poll() is None:
      sample=host_sample();samples.append(sample);check_sample(sample,baseline)
      with (r/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{sample[0]}\t{sample[1]}\n')
      if time.monotonic()-start>90:raise RuntimeError('timeout')
      time.sleep(.1)
    finally:
     if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   wall=time.monotonic()-start;assert proc.returncode==0
   timing=[[float(x) for x in line.split()] for line in (dest/'timings.tsv').read_text().splitlines()];assert len(timing)==12
   assert [int(t[0]) for t in timing]==[143,142,142,143]*3
   medians={name:{metric:statistics.median(t[index] for t in timing[4:] if int(t[0])==kind) for metric,index in [('installation_ms',2),('compute_ms',3),('readback_cleanup_ms',4),('graph_total_ms',5)]} for name,kind in [('ptq',143),('pq',142)]}
   records.append({**case,'process_wall_seconds':wall,'warm_medians':medians,'graph_total_ptq_over_pq':medians['ptq']['graph_total_ms']/medians['pq']['graph_total_ms'],'files':{p.name:digest(p) for p in dest.iterdir()}})
 except Exception as exc:error=str(exc) or type(exc).__name__
 result={'experiment':'AW-0095','completed':len(records)==6 and error is None,'error':error,'records':records,'plan_sha256':digest(r/'plan.json'),'pressure_peak':max(s[0] for s in samples),'swap_growth_peak_mib':max(0,max(s[1] for s in samples)-baseline),'pressure_sha256':digest(r/'pressure.tsv'),'thermal_after':subprocess.check_output(['pmset','-g','therm'],text=True),'external_evidence':str(r),'scope':plan['scope']}
 result['screen_retained']=result['completed'] and all(rec['warm_medians']['ptq']['compute_ms']/rec['warm_medians']['pq']['compute_ms']>1 for rec in records if rec['columns']==1)
 (r/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
