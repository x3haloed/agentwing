#!/usr/bin/env python3
"""AW185 fixed-bit norm-corrected actual V/attention CPU rejection screen."""
import ctypes,json,subprocess
from pathlib import Path
import numpy as np
import check_bonsai_attention_oracle as oracle
from run_local_agent import ROOT,digest,host_sample,check_sample,preflight
R=Path('/Users/chad/Models/agentwing/evidence/AW-0185');E=R.parent

def main():
 assert not (R/'plan.json').exists();preflight();baseline=host_sample();authority=json.loads((ROOT/'evidence/AW-0184-turbo4-codebook-screen.json').read_text());oracle.CAPTURE=E/'AW-0109';tensors=oracle.read_capture()
 lib=ctypes.CDLL(str(R/'codec.dylib'));f=lib.encode_book;ptr=ctypes.POINTER(ctypes.c_float);f.argtypes=[ptr,ctypes.c_int,ptr,ptr,ctypes.c_void_p,ptr];f.restype=None
 basepath=Path('/Users/chad/Models/agentwing/runtime-builds/prism-turbo-mixed-graph/bin/libggml-base.0.21.0.dylib');base=ctypes.CDLL(str(basepath));native=base.quantize_row_turbo4_0_ref;native.argtypes=[ptr,ctypes.c_void_p,ctypes.c_int64];native.restype=None
 tables={'native':(authority['plan']['old_centroids'],authority['plan']['old_thresholds']),'candidate':(authority['result']['candidate_centroids'],authority['result']['candidate_thresholds'])}
 plan={'experiment':'AW-0185','hypothesis':'AW184 stationary Gaussian table lowers actual norm-corrected V and attention error at unchanged128group/68byte4bit layout','acceptance':'Baseline packed encoder bitexact native; finite full decoded vectors; candidate V and attention relativeL2 lower in each layer3/31/63. Reject any layer regression before GPU integration. CPU cost not performance evidence.','source_sha256':digest(ROOT/'experiments/fixtures/bonsai-codebook-codec.cpp'),'runner_sha256':digest(Path(__file__)),'codec_sha256':digest(R/'codec.dylib'),'base_sha256':digest(basepath),'codebook_authority_sha256':digest(ROOT/'evidence/AW-0184-turbo4-codebook-screen.json'),'capture_authority_sha256':digest(E/'AW-0109/result.json'),'oracle_source_sha256':digest(ROOT/'scripts/check_bonsai_attention_oracle.py'),'tables':tables,'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'storage':'internalSSD','scope':'CPU actual own32 captured V/attention; table derived without task data. No fresh candidate trajectory, kernel speed, vision/tool/endpoint qualification'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');records=[]
 for layer in [3,31,63]:
  q=np.array([[oracle.value(tensors[layer,0],d,0,h) for d in range(256)] for h in range(24)],dtype=float);keys=np.array([[[oracle.value(tensors[layer,1],d,t,h) for d in range(256)] for t in range(48)] for h in range(4)],dtype=float);values=np.array([[[oracle.value(tensors[layer,2],d,t,h) for d in range(256)] for t in range(48)] for h in range(4)],dtype='<f4');assert tensors[layer,0]['scale']==.0625
  def attention(v):
   outputs=[]
   for h in range(24):
    scores=keys[h//6]@q[h]*.0625;w=np.exp(scores-scores.max());w/=w.sum();outputs.append(w@v[h//6].astype(float))
   return np.array(outputs)
  reference=attention(values);(R/f'{layer}-input.bin').write_bytes(values.tobytes());(R/f'{layer}-reference.bin').write_bytes(reference.astype('<f8').tobytes());row={'layer':layer}
  for arm,(centers,cuts) in tables.items():
   c=np.array(centers,dtype='<f4');t=np.array(cuts,dtype='<f4');packed=ctypes.create_string_buffer(values.size//128*68);out=np.empty_like(values);f(values.ctypes.data_as(ptr),values.size,c.ctypes.data_as(ptr),t.ctypes.data_as(ptr),packed,out.ctypes.data_as(ptr));assert np.isfinite(out).all()
   if arm=='native':
    control=ctypes.create_string_buffer(len(packed));native(values.ctypes.data_as(ptr),control,values.size);assert packed.raw==control.raw,'Native encoder parity failed'
   result=attention(out);(R/f'{layer}-{arm}-packed.bin').write_bytes(packed.raw);(R/f'{layer}-{arm}-decoded.bin').write_bytes(out.tobytes());(R/f'{layer}-{arm}-attention.bin').write_bytes(result.astype('<f8').tobytes());row[arm]={'V_relative_l2':float(np.linalg.norm(out.astype(float)-values)/np.linalg.norm(values)),'attention_relative_l2':float(np.linalg.norm(result-reference)/np.linalg.norm(reference))}
  row['passed']=all(row['candidate'][key]<row['native'][key] for key in ['V_relative_l2','attention_relative_l2']);records.append(row)
 after=host_sample();check_sample(after,baseline[1]);result={'experiment':'AW-0185','passed':all(x['passed'] for x in records),'records':records,'phase_host_samples':[baseline,after],'plan_sha256':digest(R/'plan.json'),'raw_sha256':{p.name:digest(p) for p in R.iterdir() if p.is_file()},'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['records'],indent=2))
if __name__=='__main__':main()
