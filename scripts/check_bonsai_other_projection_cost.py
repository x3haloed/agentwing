#!/usr/bin/env python3
"""AW-0094 projection cost screen; never endpoint utility evidence."""
import ctypes,hashlib,fcntl,json,subprocess,time,os,signal,statistics
from pathlib import Path
from read_bonsai_tensor_directory import inspect
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample
r=Path('/Users/chad/Models/agentwing/evidence/AW-0094');w=r/'weights';c=Path('/Users/chad/Models/agentwing/evidence/AW-0093')
preflight()
with (ROOT/'var/model-owner.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 cp=json.loads((c/'plan.json').read_text());model=Path('/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-PTQ1_0.gguf')
 library=Path('/Users/chad/Models/agentwing/evidence/AW-0086/repack.dylib');assert digest(library)=="c1a0409f59334d35bfd08ad5362bee4f56bad24f065b3fbd42f0b9cb2ca54784"
 preparation={'source_sha256':digest(Path(__file__)),'repack_sha256':digest(library),'capture_plan_sha256':digest(c/'plan.json'),'selection':cp['required_projections'],'expected_model_sha256':cp['model_sha256'],'condition':'Warm uncontrolled internal SSD, bounded single-tensor conversion'}
 assert not (r/'preparation-plan.json').exists();(r/'preparation-plan.json').write_text(json.dumps(preparation,indent=2)+'\n')
 sha=hashlib.sha256()
 with model.open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024*1024),b''):sha.update(chunk)
 assert sha.hexdigest()==cp['model_sha256'];directory=inspect(model);w.mkdir();prior={'records':[]};pack=ctypes.CDLL(str(library)).repack_ptq_blocks;pack.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];pack.restype=ctypes.c_int
 prepbaseline=host_sample()[1];prep_samples=[]
 with model.open('rb') as f:
  for name in cp['required_projections']:
   current=host_sample();check_sample(current,prepbaseline);prep_samples.append(current)
   tensor=next(t for t in directory['tensors'] if t['name']==name);assert tensor['type']==143;size=tensor['elements']//128*28;dest=w/name;dest.mkdir();begin=time.monotonic();f.seek(directory['data_offset']+tensor['relative_offset']);data=f.read(size);assert len(data)==size;read=time.monotonic();output=ctypes.create_string_buffer(size//28*34);assert pack(data,size,output,len(output))==1;converted=time.monotonic();(dest/'ptq.bin').write_bytes(data);(dest/'pq.bin').write_bytes(output.raw);written=time.monotonic()
   prior['records'].append({'tensor':name,'dimensions':tensor['dimensions'],'files':{p.name:digest(p) for p in dest.iterdir()},'preparation_seconds':{'read':read-begin,'allocation_conversion':converted-read,'write':written-converted},'ptq_bytes':size,'pq_bytes':len(output)})
   del data,output;current=host_sample();check_sample(current,prepbaseline);prep_samples.append(current)
 (r/'weights-receipt.json').write_text(json.dumps(prior,indent=2)+'\n')

 for n,h in cp['libraries'].items():assert digest(ROOT/'var/bonsai-demo/bin/mac'/n)==h
 cases=[]
 for i,rec in enumerate(prior['records']):
  for n in ['ptq.bin','pq.bin']:assert digest(w/rec['tensor']/n)==rec['files'][n]
  cases.extend({'tensor':rec['tensor'],'capture_index':i,'dimensions':rec['dimensions'],'columns':columns} for columns in [1,16])
 plan={'experiment':'AW-0094','cases':cases,'order':'ABBA repeated 3 times per case; first ABBA warmup retained but excluded from steady diagnostic','metrics':['installation_ms','compute_ms','readback_cleanup_ms','graph_total_ms','process_wall_seconds'],'rule':'Retain for whole-model screen only if median warm graph total PTQ/PQ >1 in at least one tested operation; no promotion','timeout_seconds':90,'source_sha256':digest(ROOT/'experiments/fixtures/bonsai-packing-cost.cpp'),'script_sha256':digest(Path(__file__)),'binary_sha256':digest(r/'packing-cost'),'libraries':cp['libraries'],'weights_receipt_sha256':digest(r/'weights-receipt.json'),'capture_receipt_sha256':digest(c/'result.json'),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),'thermal_before':subprocess.check_output(['pmset','-g','therm'],text=True),'cache':'OS page/shader cache uncontrolled; source files warm; fresh Metal backend per case','scope':'Real dense FFN-up operation cost only, not full storage/install/unified-memory/full-model or agent endpoint cost'}
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
 result={'experiment':'AW-0094','completed':len(records)==12 and error is None,'error':error,'records':records,'plan_sha256':digest(r/'plan.json'),'pressure_peak':max(s[0] for s in samples),'swap_growth_peak_mib':max(0,max(s[1] for s in samples)-baseline),'pressure_sha256':digest(r/'pressure.tsv'),'thermal_after':subprocess.check_output(['pmset','-g','therm'],text=True),'external_evidence':str(r),'scope':plan['scope'],'preparation_host_samples':prep_samples,'preparation_plan_sha256':digest(r/'preparation-plan.json'),'preparation':prior}
 (r/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
