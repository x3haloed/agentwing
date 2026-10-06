#!/usr/bin/env python3
"""AW-0117 native cache writer ABI, reverse-index and reconstruction screen."""
import ctypes,json,math,re,struct,subprocess,shutil,time,os,signal
from pathlib import Path
import check_bonsai_attention_oracle as oracle
from run_local_agent import preflight,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0117');E=R.parent

def main():
 preflight();baseline=host_sample();R.mkdir(exist_ok=True)
 header=(E/'AW-0114/ggml-metal-impl.h').read_text();end=header.index('} ggml_metal_kargs_set_rows;');start=header.rfind('typedef struct {',0,end)
 fields=re.findall(r'(int32_t|uint64_t)\s+(\w+);',header[start:end]);types={'int32_t':ctypes.c_int32,'uint64_t':ctypes.c_uint64}
 class Args(ctypes.Structure):_fields_=[(name,types[kind]) for kind,name in fields]
 oracle.CAPTURE=E/'AW-0109';tensors=oracle.read_capture()
 for bits,size in [(3,100),(4,136)]:
  for layer in [3,31,63]:
   d=R/f'{layer}-{bits}';d.mkdir(exist_ok=True);v=tensors[layer,2]
   values=[oracle.value(v,i,t,h) for h in range(4) for t in range(48) for i in range(256)];assert all(math.isfinite(x) for x in values)
   (d/'input.bin').write_bytes(struct.pack('<49152f',*values));(d/'indices.bin').write_bytes(struct.pack('<192q',*reversed(range(192))))
   a=Args();params={'nk0':2,'ne01':192,'nb01':1024,'nb02':192*1024,'nb03':192*1024,'ne11':1,'ne12':1,'nb10':8,'nb11':1536,'nb12':1536,'nb1':size,'nb2':192*size,'nb3':192*size}
   for name,value in params.items():setattr(a,name,value)
   (d/'args.bin').write_bytes(bytes(a))
 swift=Path('experiments/fixtures/turbo-cache-writer.swift');binary=R/'writer';command=['swiftc','-O',str(swift),'-o',str(binary)];build=subprocess.run(command,capture_output=True,text=True);(R/'compile.log').write_text(build.stdout+build.stderr);assert build.returncode==0
 plan={'experiment':'AW-0117','harness_sha256':oracle.digest(__file__),'swift_sha256':oracle.digest(swift),'binary_sha256':oracle.digest(binary),'metal_sha256':oracle.digest(E/'AW-0115/embedded.metal'),'capture_sha256':oracle.digest(E/'AW-0109/result.json'),'packed_authority_sha256':oracle.digest(E/'AW-0110/result.json'),'inputs':{str(p.relative_to(R)):oracle.digest(p) for p in R.glob('*/*.bin')},'args_fields':fields,'args_size':ctypes.sizeof(Args),'indices':'reverse192 populated rows','threads':[32,1,1],'dispatch':[192,1,1],'acceptance':'Each native writer reconstruction finite and relative L2<=.005 against CPU encoding at reverse-mapped indices;256-byte prefix/suffix canaries unchanged. No model quality acceptance.','timeout_seconds':90,'scope':'GPU Turbo3/4 cache writer real populated V rows only; no cache graph registration or model generation integration'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');samples=[];error=None;start=time.monotonic()
 with (R/'writer.log').open('w') as log:
  proc=subprocess.Popen([str(binary),str(E/'AW-0115/embedded.metal'),str(R)],stdout=log,stderr=log,start_new_session=True)
  try:
   while proc.poll() is None:
    sample=host_sample();samples.append(sample);check_sample(sample,baseline[1])
    if time.monotonic()-start>90:raise RuntimeError('timeout')
    time.sleep(.25)
  except Exception as exc:error=str(exc)
  finally:
   if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 libpath=E/'AW-0105/turbo-codec.dylib';lib=ctypes.CDLL(str(libpath));records=[]
 authority=json.loads((E/'AW-0110/result.json').read_text())
 if proc.returncode==0 and not error:
  for bits,size in [(3,100),(4,136)]:
   fn=getattr(lib,f'dequantize_row_turbo{bits}_0');fn.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_float),ctypes.c_int64];fn.restype=None
   def decode(data):
    buf=ctypes.create_string_buffer(data);out=(ctypes.c_float*49152)();fn(buf,out,49152);return list(out)
   for layer in [3,31,63]:
    d=R/f'{layer}-{bits}';raw=(d/'output.bin').read_bytes();canaries=raw[:256]==raw[-256:]==b'\xa5'*256;packed=raw[256:-256];p=E/'AW-0110'/f'{layer}-turbo{bits}-v.bin';ref=p.read_bytes();assert oracle.digest(p)==next(x['packed_value_sha256'] for x in authority['records'] if x['layer']==layer and x['value_format']==f'turbo{bits}')
    reversed_ref=b''.join(ref[i*size:(i+1)*size] for i in reversed(range(192)));a=decode(packed);b=decode(reversed_ref);finite=all(math.isfinite(x) for x in a);relative=math.sqrt(math.fsum((x-y)**2 for x,y in zip(a,b))/math.fsum(x*x for x in b)) if finite else None
    records.append({'layer':layer,'bits':bits,'relative_l2':relative,'byte_identical_cpu_reverse_encoding':packed==reversed_ref,'canaries':canaries,'finite':finite,'passed':canaries and finite and relative<=.005,'output_sha256':oracle.digest(d/'output.bin')})
 result={'experiment':'AW-0117','exit':proc.returncode,'error':error,'passed':len(records)==6 and all(x['passed'] for x in records),'records':records,'pressure_peak':max(x[0] for x in samples),'swap_growth_peak_mib':max(0,max(x[1] for x in samples)-baseline[1]),'plan_sha256':oracle.digest(R/'plan.json'),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
