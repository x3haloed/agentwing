#!/usr/bin/env python3
"""AW-0113 actual compressed attention aggregate with upstream Metal inverse."""
import ctypes,json,math,struct,subprocess
from pathlib import Path
import check_bonsai_attention_oracle as oracle
from run_local_agent import preflight,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0113');E=R.parent

def main():
 preflight();baseline=host_sample();R.mkdir(exist_ok=True)
 authority=json.loads((E/'AW-0110/result.json').read_text());assert len(authority['baseline_records'])==3
 prior=json.loads((E/'AW-0112/result.json').read_text());assert prior['passed']
 binary=E/'AW-0112/wht-metal';source=E/'AW-0112/extracted.metal';libpath=E/'AW-0105/turbo-codec.dylib';basepath=Path('var/bonsai-demo/bin/mac/libggml-base.0.21.0.dylib').resolve()
 plan={'experiment':'AW-0113','harness_sha256':oracle.digest(__file__),'capture_sha256':oracle.digest(E/'AW-0109/result.json'),'packed_authority_sha256':oracle.digest(E/'AW-0110/result.json'),'metal_authority_sha256':oracle.digest(E/'AW-0112/result.json'),'binary_sha256':oracle.digest(binary),'metal_sha256':oracle.digest(source),'codec_sha256':oracle.digest(libpath),'base_sha256':oracle.digest(basepath),'acceptance':'Each complete aggregate: CPU after-weight inverse versus weighted per-row inverse L2<=1e-6; native Metal inverse versus CPU<=.005; missing inverse negative>.25; all finite. Not model quality acceptance.','scope':'CPU compressed q8 K/Turbo3/4 V attention aggregate, actual48-token candidate-generated FP16 trajectory; only inverse bookend on Metal, not GPU attention or compressed trajectory'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 turbo=ctypes.CDLL(str(libpath));base=ctypes.CDLL(str(basepath));inverse=turbo.turbo_cpu_fwht_inverse;inverse.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_int];inverse.restype=None
 def inv(values):
  out=(ctypes.c_float*len(values))(*values)
  for start in range(0,len(values),128):inverse(ctypes.cast(ctypes.byref(out,start*4),ctypes.POINTER(ctypes.c_float)),128)
  return list(out)
 def decode(p,lib,kind,size):
  raw=p.read_bytes();assert len(raw)==4*48*size
  f=getattr(lib,'dequantize_row_'+kind);f.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_float),ctypes.c_int64];f.restype=None;rows=[]
  for h in range(4):
   head=[]
   for t in range(48):
    buf=ctypes.create_string_buffer(raw[(h*48+t)*size:(h*48+t+1)*size]);out=(ctypes.c_float*256)();f(buf,out,256);head.append(list(out))
   rows.append(head)
  return rows
 oracle.CAPTURE=E/'AW-0109';tensors=oracle.read_capture();records=[]
 for layer in [3,31,63]:
  q,mask=tensors[layer,0],tensors[layer,3];kp=E/f'AW-0110/{layer}-q8-k.bin';keys=decode(kp,base,'q8_0',272)
  weights=[]
  for h in range(24):
   assert [i for i in range(256) if math.isfinite(oracle.value(mask,i,0))]==list(range(48))
   query=[oracle.value(q,d,0,h) for d in range(256)];scores=[q['scale']*math.fsum(a*b for a,b in zip(query,keys[h//6][t])) for t in range(48)];maximum=max(scores);w=[math.exp(s-maximum) for s in scores];norm=math.fsum(w);weights.append([x/norm for x in w])
  for bits,size in [(3,100),(4,136)]:
   vp=E/f'AW-0110/{layer}-turbo{bits}-v.bin'
   record=next(x for x in authority['records'] if x['layer']==layer and x['value_format']==f'turbo{bits}');assert oracle.digest(vp)==record['packed_value_sha256']
   vals=decode(vp,turbo,f'turbo{bits}_0',size);decoded=[[inv(row) for row in head] for head in vals]
   def aggregate(v):return [math.fsum(weights[h][t]*v[h//6][t][d] for t in range(48)) for h in range(24) for d in range(256)]
   rotated=aggregate(vals);reference=aggregate(decoded);cpu=inv(rotated)
   def error(v):return math.sqrt(math.fsum((a-b)**2 for a,b in zip(v,reference))/math.fsum(x*x for x in reference))
   p=R/f'{layer}-turbo{bits}-aggregate.bin';p.write_bytes(struct.pack('<'+'f'*len(rotated),*rotated));target=R/f'{layer}-turbo{bits}-metal.bin'
   run=subprocess.run([str(binary),str(source),str(p),str(target),'1'],capture_output=True,text=True,timeout=60);assert run.returncode==0,(run.stdout,run.stderr)
   metal=struct.unpack('<'+'f'*len(rotated),target.read_bytes());assert all(math.isfinite(x) for x in metal)
   cpu_error=error(cpu);metal_error=error(metal);negative=error(rotated)
   records.append({'layer':layer,'value_bits':bits,'values':len(rotated),'cpu_aggregate_inverse_relative_l2':cpu_error,'metal_aggregate_inverse_relative_l2':metal_error,'missing_inverse_relative_l2':negative,'passed':cpu_error<=1e-6 and metal_error<=.005 and negative>.25,'key_sha256':oracle.digest(kp),'value_sha256':oracle.digest(vp),'output_sha256':oracle.digest(target)})
   check_sample(host_sample(),baseline[1])
 result={'experiment':'AW-0113','passed':len(records)==6 and all(x['passed'] for x in records),'records':records,'plan_sha256':oracle.digest(R/'plan.json'),'phase_host_samples':[baseline,host_sample()],'os':subprocess.check_output(['sw_vers'],text=True),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
