#!/usr/bin/env python3
"""AW-0105 standalone codec ABI/bounds smoke; not KV quality acceptance."""
import ctypes,hashlib,json,math,random,subprocess
from pathlib import Path
from run_local_agent import preflight,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0105')
def main():
 preflight();baseline=host_sample();lib=ctypes.CDLL(str(R/'turbo-codec.dylib'));ctypes.c_int.in_dll(lib,'turbo3_cpu_wht_group_size').value=128
 inverse=lib.turbo_cpu_fwht_inverse;inverse.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_int]
 rng=random.Random(105);patterns={'zero':[0.0]*256,'one_hot':[1.0]+[0.0]*255,'sine':[math.sin(i*.17) for i in range(256)],'gaussian':[rng.gauss(0,1) for _ in range(256)]};records=[]
 smokeplan={'experiment':'AW-0105','patterns':list(patterns),'head_dimension':256,'rotation_groups_per_head':2,'group_size':128,'packed_bytes':{'turbo2':68,'turbo3':100,'turbo4':136},'acceptance':'Canaries unchanged, repeated encoding byte-identical, all reconstructions finite; reconstruction error diagnostic only','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'library_sha256':hashlib.sha256((R/'turbo-codec.dylib').read_bytes()).hexdigest(),'scope':'Block ABI and bounds only; two128 groups, no full K/V attention or Metal graph'}
 assert not (R/'smoke-plan.json').exists();(R/'smoke-plan.json').write_text(json.dumps(smokeplan,indent=2)+'\n')
 for bits,size in [(2,68),(3,100),(4,136)]:
  quant=getattr(lib,f'quantize_row_turbo{bits}_0_ref');quant.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_void_p,ctypes.c_int64];quant.restype=None
  dequant=getattr(lib,f'dequantize_row_turbo{bits}_0');dequant.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_float),ctypes.c_int64];dequant.restype=None
  for name,values in patterns.items():
   source=(ctypes.c_float*256)(*values);results=[]
   for repeat in range(2):
    raw=ctypes.create_string_buffer(b'\xa5'*16+b'\xcc'*size+b'\x5a'*16);ptr=ctypes.c_void_p(ctypes.addressof(raw)+16);quant(source,ptr,256);assert raw.raw[:16]==b'\xa5'*16 and raw.raw[16+size:32+size]==b'\x5a'*16
    packed=raw.raw[16:16+size];results.append(packed);out=(ctypes.c_float*256)();dequant(ptr,out,256)
    for start in [0,128]:inverse(ctypes.cast(ctypes.byref(out,start*4),ctypes.POINTER(ctypes.c_float)),128)
    assert all(math.isfinite(v) for v in out)
   assert results[0]==results[1];norm=math.fsum(float(v)*v for v in source);error=math.sqrt(math.fsum((float(a)-float(b))**2 for a,b in zip(source,out))/norm) if norm else max(abs(float(v)) for v in out)
   records.append({'format':f'turbo{bits}','pattern':name,'packed_bytes':size,'finite':True,'deterministic':True,'canaries_unchanged':True,'reconstruction_relative_l2_or_zero_absolute':error,'packed_sha256':hashlib.sha256(results[0]).hexdigest()})
 after=host_sample();check_sample(after,baseline[1]);result={'experiment':'AW-0105','passed':len(records)==12,'records':records,'smoke_plan_sha256':hashlib.sha256((R/'smoke-plan.json').read_bytes()).hexdigest(),'host_phase_samples':[baseline,after],'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'external_evidence':str(R),'scope':smokeplan['scope'],'limitations':'No numeric accuracy gate, performance metric, continuous pressure sampling, GGML type registration, Metal dispatch or model integration'}
 (R/'smoke-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
