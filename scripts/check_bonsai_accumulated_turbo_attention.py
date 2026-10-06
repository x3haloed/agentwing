#!/usr/bin/env python3
"""AW-0110 real causal attention distortion screen, not runtime acceptance."""
import ctypes,json,math,subprocess
from pathlib import Path
from check_bonsai_attention_oracle import read_capture,value,digest,CAPTURE
from run_local_agent import preflight,host_sample,check_sample
CAPTURE=Path('/Users/chad/Models/agentwing/evidence/AW-0109')
R=Path('/Users/chad/Models/agentwing/evidence/AW-0110')
def read_accumulated():
 import check_bonsai_attention_oracle as oracle
 oracle.CAPTURE=CAPTURE
 return oracle.read_capture()
def main():
 preflight();baseline=host_sample();R.mkdir(exist_ok=True)
 turbo_path=CAPTURE.parent/'AW-0105/turbo-codec.dylib';base_path=Path('var/bonsai-demo/bin/mac/libggml-base.0.21.0.dylib').resolve()
 prior=json.loads((CAPTURE.parent/'AW-0105/smoke-plan.json').read_text());assert digest(turbo_path)==prior['library_sha256']
 authority=json.loads((CAPTURE.parent/'AW-0107/result.json').read_text());assert authority['passed']
 plan={'experiment':'AW-0110','script_sha256':digest(__file__),'capture_sha256':digest(CAPTURE/'result.json'),'oracle_sha256':digest(CAPTURE.parent/'AW-0107/result.json'),'turbo_library_sha256':digest(turbo_path),'prism_base_sha256':digest(base_path),'layers':[3,31,63],'baseline_oracle_limit':1e-3,'provisional_distortion_limit':0.25,'acceptance':'Each layer relative attention-output L2<=0.25 against independent FP16 CPU attention; finite reconstruction; canaries intact. This cheap rejection threshold is not model-quality acceptance.','scope':'Actual final decode after32 candidate-generated tokens; q8 K and Turbo2/3/4 V, two128 WHT groups per256 head; CPU only, no Metal/cache integration'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 turbo=ctypes.CDLL(str(turbo_path));base=ctypes.CDLL(str(base_path));ctypes.c_int.in_dll(turbo,'turbo3_cpu_wht_group_size').value=128
 inverse=turbo.turbo_cpu_fwht_inverse;inverse.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_int];inverse.restype=None
 def codec(rows,lib,kind,size,rotate=False):
  quant=getattr(lib,'quantize_row_'+kind+'_ref');dequant=getattr(lib,'dequantize_row_'+kind)
  quant.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_void_p,ctypes.c_int64];dequant.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_float),ctypes.c_int64];quant.restype=dequant.restype=None
  decoded=[];packed=bytearray()
  for head in rows:
   restored=[]
   for row in head:
    src=(ctypes.c_float*256)(*row);raw=ctypes.create_string_buffer(b'\xa5'*16+b'\xcc'*size+b'\x5a'*16);ptr=ctypes.c_void_p(ctypes.addressof(raw)+16);quant(src,ptr,256)
    assert raw.raw[:16]==b'\xa5'*16 and raw.raw[16+size:32+size]==b'\x5a'*16
    packed.extend(raw.raw[16:16+size]);out=(ctypes.c_float*256)();dequant(ptr,out,256)
    if rotate:
     for start in [0,128]:inverse(ctypes.cast(ctypes.byref(out,start*4),ctypes.POINTER(ctypes.c_float)),128)
    assert all(math.isfinite(x) for x in out);restored.append(list(out))
   decoded.append(restored)
  return decoded,bytes(packed)
 tensors=read_accumulated();records=[];baseline_records=[]
 for layer in plan['layers']:
  q,k,v,mask,out=[tensors[layer,i] for i in range(5)]
  assert q['ne']==[256,1,24,1] and out['ne']==[256,24,1,1]
  active_keys=[i for i in range(256) if math.isfinite(value(mask,i,0))];assert active_keys==list(range(48))
  queries=[[[value(q,d,t,h) for d in range(256)] for t in range(1)] for h in range(24)]
  keys=[[[value(k,d,t,h) for d in range(256)] for t in range(48)] for h in range(4)];vals=[[[value(v,d,t,h) for d in range(256)] for t in range(48)] for h in range(4)]
  def attention(kk,vv):
   result=[]
   for h in range(24):
    for token in range(1):
     active=[i for i in range(256) if math.isfinite(value(mask,i,token))];assert active==active_keys
     scores=[q['scale']*math.fsum(a*b for a,b in zip(queries[h][token],kk[h//6][i]))+value(mask,i,token) for i in active];maximum=max(scores);w=[math.exp(s-maximum) for s in scores];norm=math.fsum(w);w=[x/norm for x in w]
     result.extend(math.fsum(weight*vv[h//6][i][d] for i,weight in zip(active,w)) for d in range(256))
   return result
  reference=attention(keys,vals);norm=math.fsum(x*x for x in reference)
  native=[value(out,d,h,0) for h in range(24) for d in range(256)]
  baseline_error=math.sqrt(math.fsum((a-b)**2 for a,b in zip(native,reference))/norm)
  assert baseline_error<=1e-3
  baseline_records.append({'layer':layer,'native_vs_cpu_relative_l2':baseline_error,'active_keys':len(active_keys)})
  quant_keys,packed=codec(keys,base,'q8_0',272);(R/f'{layer}-q8-k.bin').write_bytes(packed)
  for bits,size in [(2,68),(3,100),(4,136)]:
   quant_vals,packed=codec(vals,turbo,f'turbo{bits}_0',size,True);p=R/f'{layer}-turbo{bits}-v.bin';p.write_bytes(packed)
   candidate=attention(quant_keys,quant_vals);relative=math.sqrt(math.fsum((a-b)**2 for a,b in zip(candidate,reference))/norm)
   records.append({'layer':layer,'key_format':'q8_0','value_format':f'turbo{bits}','output_values':len(candidate),'relative_l2':relative,'survives_provisional_screen':relative<=0.25,'packed_value_sha256':digest(p)})
  check_sample(host_sample(),baseline[1])
 result={'experiment':'AW-0110','records':records,'baseline_records':baseline_records,'plan_sha256':digest(R/'plan.json'),'host_phase_samples':[baseline,host_sample()],'os':subprocess.check_output(['sw_vers'],text=True),'scope':plan['scope'],'disposition':'Component screen only; no endpoint promotion'}
 (R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
