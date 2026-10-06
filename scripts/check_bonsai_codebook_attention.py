#!/usr/bin/env python3
"""AW189 real Metal-written cache consumer: full attention+inverse, ABBA."""
import ctypes,fcntl,json,subprocess,time,re,statistics
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group
R=Path('/Users/chad/Models/agentwing/evidence/AW-0189');E=R.parent

def main():
 assert not (R/'plan.json').exists();preflight();writer=json.loads((ROOT/'evidence/AW-0188-codebook-writer-long-screen.json').read_text());assert writer['result']['numeric_passed'] and writer['result']['cost_gate_passed'];builds=writer['plan']['builds'];order=[]
 for arm,b in builds.items():
  for n,h in b['libraries_sha256'].items():assert digest(Path(b['build_directory'])/'bin'/n)==h
  lib=ctypes.CDLL(str(Path(b['build_directory'])/'bin/libggml-base.0.21.0.dylib'));ptr=ctypes.POINTER(ctypes.c_float);inv=lib.turbo_cpu_fwht_inverse;inv.argtypes=[ptr,ctypes.c_int];inv.restype=None
  for layer in [3,31,63]:
   w=next(x for x in writer['result']['rows'] if x['layer']==layer and x['arm']==arm);path=E/'AW-0188'/f"{w['index']}-{arm}.bin";assert digest(path)==w['output_sha256'];packed=np.frombuffer(path.read_bytes(),dtype=np.uint8).reshape(192,136)[::-1].copy().reshape(4,48,136);vraw=b''.join(packed[h].tobytes()+bytes(16*136) for h in range(4));v=np.empty(4*64*256,dtype='<f4');fn=lib.dequantize_row_turbo4_0;fn.argtypes=[ctypes.c_void_p,ptr,ctypes.c_int64];fn.restype=None;src=ctypes.create_string_buffer(vraw);fn(src,v.ctypes.data_as(ptr),v.size)
   for i in range(0,v.size,128):inv(v[i:].ctypes.data_as(ptr),128)
   v=v.reshape(4,64,256)
   for mode in ['f16-turbo','turbo']:
    base=E/f'AW-0180/{layer}-f16-turbo-1';q=np.fromfile(base/'q.bin',dtype='<f4').reshape(24,256)
    kraw=(base/'k.bin').read_bytes() if mode=='f16-turbo' else (E/f'AW-0116/{layer}-4/k.bin').read_bytes()
    if mode=='f16-turbo':k=np.frombuffer(kraw,dtype='<f2').reshape(4,64,256).astype(float)
    else:
     k=np.empty(4*64*256,dtype='<f4');fn=lib.dequantize_row_q8_0;fn.argtypes=[ctypes.c_void_p,ptr,ctypes.c_int64];fn.restype=None;src=ctypes.create_string_buffer(kraw);fn(src,k.ctypes.data_as(ptr),k.size);k=k.reshape(4,64,256).astype(float)
    expected=[]
    for head in range(24):
     scores=k[head//6,:48]@q[head].astype(float)*.0625;weights=np.exp(scores-scores.max());weights/=weights.sum();expected.append(weights@v[head//6,:48].astype(float))
    for nq in [1,128]:
     d=R/f'{layer}-{mode}-{nq}-{arm}';d.mkdir();(d/'q.bin').write_bytes(np.repeat(q[:,None,:],nq,axis=1).astype('<f4').tobytes());(d/'k.bin').write_bytes(kraw);(d/'v.bin').write_bytes(vraw);(d/'mask.bin').write_bytes((base/'mask.bin').read_bytes());(d/'oracle.bin').write_bytes(np.tile(np.array(expected).reshape(-1),nq).astype('<f8').tobytes())
 for layer in [3,31,63]:
  for mode in ['f16-turbo','turbo']:
   for nq in [1,128]:order.extend([(layer,mode,nq,a) for a in ['control','candidate','candidate','control']])
 plan={'experiment':'AW-0189','hypothesis':'AW188 Metal-written stationary V improves actual attention with no material consumer-cost regression','acceptance':'All48exit0/fullfinite output relativeL2<=.005 against own packed float64oracle; candidate uncompressed-reference error lower every shape/mode/layer; each adjacent candidate/control median ratio<=1.10; pressure<4/swapgrowth<=1024MiB/90s watchdog. Fivewindows16full attention+inverse+readbacks; first retainedwarmup, startup/uploads separate','source_sha256':digest(ROOT/'experiments/fixtures/bonsai-codebook-attention.cpp'),'runner_sha256':digest(Path(__file__)),'binary_sha256':{a:digest(R/a) for a in builds},'writer_authority_sha256':digest(ROOT/'evidence/AW-0188-codebook-writer-long-screen.json'),'builds':builds,'inputs_sha256':{str(p.relative_to(R)):digest(p) for p in R.rglob('*.bin')},'order':order,'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internalSSD','cache':'Fresh process/ABBA eachcase, uncontrolled warmedOS cache','scope':'Real own32 captured cache; replicated128query shape, not new causal128token prompt. Consumer primitive includes inverse/readback, priorwriter separatelycosted; no fullmodel/task/vision/tool/endpoint acceptance'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');rows=[]
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for index,(layer,mode,nq,arm) in enumerate(order):
   preflight();d=R/f'{layer}-{mode}-{nq}-{arm}';out=R/f'{index}-output.bin';logpath=R/f'{index}-native.log';baseline=host_sample()[1];samples=[];error=None;proc=None;start=time.monotonic()
   with logpath.open('w') as log:
    try:
     proc=subprocess.Popen([str(R/arm),mode,str(d),str(out),str(nq)],stdout=log,stderr=log,start_new_session=True)
     while proc.poll() is None:
      s=host_sample();samples.append(s);check_sample(s,baseline)
      with (R/f'{index}-pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
      if time.monotonic()-start>90:raise RuntimeError('timeout')
      time.sleep(.25)
    except Exception as exc:error=str(exc)
    finally:stop_group(proc)
   relative=None;quality=None
   if out.exists():
    x=np.fromfile(out,dtype='<f4').astype(float);y=np.fromfile(d/'oracle.bin',dtype='<f8');ref=np.tile(np.fromfile(E/'AW-0185'/f'{layer}-reference.bin',dtype='<f8'),nq)
    if x.shape==y.shape and np.isfinite(x).all():relative=float(np.linalg.norm(x-y)/np.linalg.norm(y));quality=float(np.linalg.norm(x-ref)/np.linalg.norm(ref))
   timings=[float(v) for v in re.findall(r'compute_readback_seconds=([\d.]+)',logpath.read_text())];passed=proc is not None and proc.returncode==0 and error is None and relative is not None and relative<=.005 and len(timings)==5
   row={'index':index,'layer':layer,'mode':mode,'n_queries':nq,'arm':arm,'exit':proc.returncode if proc else None,'error':error,'numeric_passed':passed,'oracle_relative_l2':relative,'uncompressed_attention_relative_l2':quality,'all_iteration_seconds':timings,'steady_median_seconds':statistics.median(timings[1:]) if len(timings)==5 else None,'pressure_peak':max((s[0] for s in samples),default=None),'baseline_swap_mib':baseline,'swap_growth_peak_mib':max((max(0,s[1]-baseline) for s in samples),default=None),'lifetime_seconds':time.monotonic()-start,'output_sha256':digest(out) if out.exists() else None,'log_sha256':digest(logpath)};rows.append(row);(R/f'{index}-result.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({k:row[k] for k in ['index','layer','mode','n_queries','arm','numeric_passed','oracle_relative_l2']}),flush=True)
   if not passed:break
 pairs=[]
 for i in range(0,len(rows),4):
  if i+3>=len(rows):continue
  for a,b in [(i+1,i),(i+2,i+3)]:pairs.append({'candidate_index':a,'control_index':b,'cost_ratio':rows[a]['steady_median_seconds']/rows[b]['steady_median_seconds'],'quality_passed':rows[a]['uncompressed_attention_relative_l2']<rows[b]['uncompressed_attention_relative_l2']})
 result={'experiment':'AW-0189','complete':len(rows)==48,'numeric_passed':len(rows)==48 and all(x['numeric_passed'] for x in rows),'quality_gate_passed':len(pairs)==24 and all(x['quality_passed'] for x in pairs),'cost_gate_passed':len(pairs)==24 and all(x['cost_ratio']<=1.10 for x in pairs),'rows':rows,'pairs':pairs,'unattempted':order[len(rows):],'plan_sha256':digest(R/'plan.json'),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
