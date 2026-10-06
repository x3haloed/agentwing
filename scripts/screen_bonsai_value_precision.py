#!/usr/bin/env python3
"""AW199 CPU-only higher precision rotated V rejection screen."""
import ctypes,json,math,subprocess,time
from pathlib import Path
import numpy as np
import check_bonsai_attention_oracle as oracle
from screen_bonsai_turbo4_codebook import SIGMA,evaluate,quadrature
from run_local_agent import ROOT,digest,host_sample,check_sample,preflight
R=Path('/Users/chad/Models/agentwing/evidence/AW-0199')

def main():
 preflight();assert not (R/'plan.json').exists();baseline=host_sample()
 authority=json.loads((ROOT/'evidence/AW-0184-turbo4-codebook-screen.json').read_text())
 book=authority['result']; tables={4:(book['candidate_centroids'],book['candidate_thresholds'])}
 plan={'experiment':'AW-0199','hypothesis':'Gaussian stationary 6-bit rotated, norm-corrected V reduces both real V and attention relative L2 by at least 50% in each early/middle/late fixture versus stationary4bit','acceptance':'4bit packed and decoded bytes exactly match AW185; all six relative errors reduced >=50%; packed6bit independently decoded matches encoder; quadrature Gaussian MSE agreement <=1e-5','scope':'CPU numerical screen, no runtime integration, speed, fresh behavior, vision or endpoint claim; no executed tool calls','storage':'internalSSD','model_profile_sha256':digest(ROOT/'spec/bonsai-stationary-local.json'),'harness_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_sha256':digest(ROOT/'experiments/fixtures/bonsai-precision-codec.cpp'),'runner_sha256':digest(Path(__file__)),'codec_sha256':digest(R/'codec.dylib'),'codebook_authority_sha256':digest(ROOT/'evidence/AW-0184-turbo4-codebook-screen.json'),'fixture_authority_sha256':digest(R.parent/'AW-0185/result.json'),'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'sampling_context_permissions':'not applicable: saved component fixtures, no generation/server/task execution','thermal':subprocess.run(['pmset','-g','therm'],capture_output=True,text=True).stdout,'layout':{'group':128,'header_bytes':4,'4bit_bytes':68,'6bit_bytes':100,'f16_bytes':256},'host_monitoring':'before/after CPU screen; not continuous inference admission'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 c=np.linspace(-3*SIGMA,3*SIGMA,64)
 for it in range(50000):
  cuts=(c[:-1]+c[1:])/2;_,new=evaluate(cuts,c)
  change=float(np.max(np.abs(new-c)));c=new
  if change<1e-13:break
 else:raise RuntimeError('Lloyd convergence failed')
 cuts=(c[:-1]+c[1:])/2;mse,_=evaluate(cuts,c);qmse=quadrature(cuts,c);assert abs(qmse-mse)/mse<1e-5
 tables[6]=(c.tolist(),cuts.tolist())
 lib=ctypes.CDLL(str(R/'codec.dylib'));f=lib.encode_precision_book;ptr=ctypes.POINTER(ctypes.c_float);f.argtypes=[ptr,ctypes.c_int,ctypes.c_int,ptr,ptr,ctypes.c_void_p,ptr]
 inverse=lib.turbo_cpu_fwht_inverse;inverse.argtypes=[ptr,ctypes.c_int]
 oracle.CAPTURE=R.parent/'AW-0109';tensors=oracle.read_capture();records=[];inputs={}
 for layer in [3,31,63]:
  path=R.parent/'AW-0185'/f'{layer}-input.bin';inputs[str(layer)]=digest(path);v=np.fromfile(path,dtype='<f4').reshape(4,48,256)
  q=np.array([[oracle.value(tensors[layer,0],d,0,h) for d in range(256)] for h in range(24)])
  k=np.array([[[oracle.value(tensors[layer,1],d,t,h) for d in range(256)] for t in range(48)] for h in range(4)])
  def attention(values):
   out=[]
   for h in range(24):
    scores=k[h//6]@q[h]*.0625;weights=np.exp(scores-scores.max());weights/=weights.sum();out.append(weights@values[h//6].astype(float))
   return np.array(out)
  reference=attention(v);row={'layer':layer}
  for bits,(centers,thresholds) in tables.items():
   centers=np.array(centers,dtype='<f4');thresholds=np.array(thresholds,dtype='<f4');size=4+16*bits;packed=ctypes.create_string_buffer(v.size//128*size);out=np.empty_like(v)
   start=time.monotonic();f(v.ctypes.data_as(ptr),v.size,bits,centers.ctypes.data_as(ptr),thresholds.ctypes.data_as(ptr),packed,out.ctypes.data_as(ptr));elapsed=time.monotonic()-start
   assert np.isfinite(out).all()
   if bits==4:
    assert packed.raw==(R.parent/'AW-0185'/f'{layer}-candidate-packed.bin').read_bytes()
    assert out.tobytes()==(R.parent/'AW-0185'/f'{layer}-candidate-decoded.bin').read_bytes()
   decoded=np.empty_like(out).reshape(-1,128)
   for b,d in enumerate(decoded):
    block=packed.raw[b*size:(b+1)*size];assert block[2:4]==b'\0\0';scale=float(np.frombuffer(block[:2],dtype='<f2')[0]);payload=int.from_bytes(block[4:],'little');ids=[(payload>>(i*bits))&((1<<bits)-1) for i in range(128)];d[:]=centers[ids]*np.float32(scale);inverse(d.ctypes.data_as(ptr),128)
   assert decoded.tobytes()==out.tobytes()
   result=attention(out);row[str(bits)]={'V_relative_l2':float(np.linalg.norm(out.astype(float)-v)/np.linalg.norm(v)),'attention_relative_l2':float(np.linalg.norm(result-reference)/np.linalg.norm(reference)),'cpu_encode_seconds_diagnostic_only':elapsed}
   (R/f'{layer}-{bits}-packed.bin').write_bytes(packed.raw);(R/f'{layer}-{bits}-decoded.bin').write_bytes(out.tobytes())
  row['passed']=all(row['6'][key]<=.5*row['4'][key] for key in ['V_relative_l2','attention_relative_l2']);records.append(row)
 after=host_sample();check_sample(after,baseline[1])
 result={'experiment':'AW-0199','passed':all(r['passed'] for r in records),'records':records,'tables':{str(b):{'centroids':t[0],'thresholds':t[1]} for b,t in tables.items()},'gaussian_6bit_mse':mse,'quadrature_mse':qmse,'iterations':it+1,'input_sha256':inputs,'phase_host_samples':[baseline,after],'plan_sha256':digest(R/'plan.json'),'raw_sha256':{p.name:digest(p) for p in R.iterdir() if p.is_file()},'scope':plan['scope'],'disposition':'numerical survivor only' if all(r['passed'] for r in records) else 'reject numerical screen'}
 (R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(records,indent=2))
if __name__=='__main__':main()
