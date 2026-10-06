#!/usr/bin/env python3
"""AW180: actual captured attention, independent float64 mixed-format oracle."""
import ctypes,fcntl,json,subprocess,time,shutil
from pathlib import Path
import numpy as np
import check_bonsai_attention_oracle as oracle
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group
R=Path('/Users/chad/Models/agentwing/evidence/AW-0180')
B=Path('/Users/chad/Models/agentwing/runtime-builds/prism-turbo-mixed/bin')
E=R.parent

def main():
 R.mkdir(exist_ok=False);preflight()
 oracle.CAPTURE=E/'AW-0109';tensors=oracle.read_capture()
 binary=E/'AW-0179/attention-canary';lib=ctypes.CDLL(str(B/'libggml-base.0.21.0.dylib'))
 def decoded(raw,kind):
  fn=getattr(lib,'dequantize_row_'+kind);fn.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_float),ctypes.c_int64];fn.restype=None
  src=ctypes.create_string_buffer(raw);out=(ctypes.c_float*(256*64*4))();fn(src,out,256*64*4)
  return np.ctypeslib.as_array(out).copy().reshape(4,64,256)
 inv=lib.turbo_cpu_fwht_inverse;inv.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_int];inv.restype=None
 cases=[]
 for layer in [3,31,63]:
  q=tensors[layer,0];queries=np.array([[oracle.value(q,d,0,h) for d in range(256)] for h in range(24)],dtype='<f4')
  for arm in ['q8-f16','f16-turbo']:
   src=E/f'AW-0116/{layer}-4';kraw=(src/'k.bin').read_bytes();vraw=(src/'v.bin').read_bytes()
   if arm=='q8-f16':
    keys=decoded(kraw,'q8_0');vals=np.zeros((4,64,256),dtype='<f2')
    for h in range(4):
     for t in range(48):vals[h,t]=[oracle.value(tensors[layer,2],d,t,h) for d in range(256)]
    vraw=vals.tobytes();vals=vals.astype(float)
   else:
    keys=np.zeros((4,64,256),dtype='<f2')
    for h in range(4):
     for t in range(48):keys[h,t]=[oracle.value(tensors[layer,1],d,t,h) for d in range(256)]
    kraw=keys.tobytes();keys=keys.astype(float);vals=decoded(vraw,'turbo4_0')
    for row in vals.reshape(-1,256):
     for offset in [0,128]:inv(row[offset:].ctypes.data_as(ctypes.POINTER(ctypes.c_float)),128)
    vals=vals.astype(float)
   expected=[]
   for h in range(24):
    scores=keys[h//6,:48].astype(float)@queries[h].astype(float)*q['scale'];weights=np.exp(scores-scores.max());weights/=weights.sum();expected.extend(weights@vals[h//6,:48])
   expected=np.array(expected,dtype='<f8')
   for nq in [1,128]:
    d=R/f'{layer}-{arm}-{nq}';d.mkdir();(d/'q.bin').write_bytes(np.repeat(queries[:,None,:],nq,axis=1).astype('<f4').tobytes());(d/'k.bin').write_bytes(kraw);(d/'v.bin').write_bytes(vraw);(d/'mask.bin').write_bytes(np.array([0.]*48+[-np.inf]*16,dtype='<f2').tobytes());(d/'oracle.bin').write_bytes(np.tile(expected,nq).tobytes());cases.append((layer,arm,nq,d))
 plan={'experiment':'AW-0180','scope':'Real own32 accumulated layer3/31/63 cache attention; replicated query columns exercise prefill shape, not real new128-token prompt or endpoint','acceptance':'Every native op supported; exits0; finite full outputs; relativeL2<=.005 vs independent double CPU softmax using actual decoded packed formats; host pressure<4/swap growth<=1024MiB;90s per case','source_sha256':digest(ROOT/'experiments/fixtures/bonsai-mixed-attention.cpp'),'runner_sha256':digest(Path(__file__)),'oracle_helper_sha256':digest(ROOT/'scripts/check_bonsai_attention_oracle.py'),'binary_sha256':digest(binary),'build_authority_sha256':digest(ROOT/'evidence/AW-0179-mixed-cache-build.json'),'capture_authority_sha256':digest(E/'AW-0109/result.json'),'libraries_sha256':{p.name:digest(p) for p in B.glob('*.dylib')},'input_sha256':{str(p.relative_to(R)):digest(p) for p in R.rglob('*.bin')},'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internalSSD','cache':'Fresh process per case; uncontrolled warm OS cache; no speed comparison','order':[(l,a,n) for l,a,n,d in cases]}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');rows=[]
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for layer,arm,nq,d in cases:
   preflight();baseline=host_sample()[1];samples=[];error=None;proc=None;start=time.monotonic()
   with (d/'native.log').open('w') as log:
    try:
     proc=subprocess.Popen([str(binary),arm,str(d),str(d/'output.bin'),str(nq)],stdout=log,stderr=log,start_new_session=True)
     while proc.poll() is None:
      s=host_sample();samples.append(s);check_sample(s,baseline)
      with (d/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
      if time.monotonic()-start>90:raise RuntimeError('timeout')
      time.sleep(.25)
    except Exception as exc:error=str(exc)
    finally:stop_group(proc)
   relative=None
   if (d/'output.bin').exists():
    x=np.fromfile(d/'output.bin',dtype='<f4').astype(float);y=np.fromfile(d/'oracle.bin',dtype='<f8')
    if x.shape==y.shape and np.isfinite(x).all():relative=float(np.linalg.norm(x-y)/np.linalg.norm(y))
   row={'layer':layer,'arm':arm,'n_queries':nq,'exit':proc.returncode if proc else None,'error':error,'relative_l2':relative,'passed':proc is not None and proc.returncode==0 and error is None and relative is not None and relative<=.005,'pressure_peak':max((s[0] for s in samples),default=None),'baseline_swap_mib':baseline,'swap_growth_peak_mib':max((max(0,s[1]-baseline) for s in samples),default=None),'lifetime_seconds':time.monotonic()-start,'raw_sha256':{p.name:digest(p) for p in d.iterdir() if p.is_file()}}
   (d/'result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(json.dumps({k:v for k,v in row.items() if k!='raw_sha256'}),flush=True)
   if not row['passed']:break
 (R/'result.json').write_text(json.dumps({'experiment':'AW-0180','passed':len(rows)==12 and all(x['passed'] for x in rows),'rows':rows,'unattempted':plan['order'][len(rows):],'plan_sha256':digest(R/'plan.json')},indent=2)+'\n')

if __name__=='__main__':main()
