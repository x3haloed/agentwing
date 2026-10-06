#!/usr/bin/env python3
"""AW-0119 unchanged native compressed Metal attention against actual CPU authority."""
import ctypes,json,math,re,struct,subprocess,shutil,time,os,signal
from pathlib import Path
import check_bonsai_attention_oracle as oracle
from run_local_agent import preflight,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0119');E=R.parent

def main():
 preflight();baseline=host_sample();R.mkdir(exist_ok=True)
 header=(E/'AW-0114/ggml-metal-impl.h').read_text();decl=header[header.index('typedef struct {',header.index('} ggml_metal_kargs_flash_attn_ext;')):header.index('} ggml_metal_kargs_flash_attn_ext_vec;')]
 fields=re.findall(r'(int32_t|uint64_t|float)\s+(\w+);',decl);types={'int32_t':ctypes.c_int32,'uint64_t':ctypes.c_uint64,'float':ctypes.c_float}
 class Args(ctypes.Structure):_fields_=[(name,types[kind]) for kind,name in fields]
 oracle.CAPTURE=E/'AW-0109';tensors=oracle.read_capture()
 for bits,size in [(3,100),(4,136)]:
  for layer in [3,31,63]:
   d=R/f'{layer}-{bits}';d.mkdir(exist_ok=True);q=tensors[layer,0]
   values=[oracle.value(q,i,0,h) for h in range(24) for i in range(256)];(d/'q.bin').write_bytes(struct.pack('<6144f',*values))
   for kind,row_size in [('k',272),('v',size)]:
    p=E/'AW-0110'/f'{layer}-q8-k.bin' if kind=='k' else E/'AW-0110'/f'{layer}-turbo{bits}-v.bin'
    raw=p.read_bytes();assert len(raw)==4*48*row_size
    padded=b''.join(raw[h*48*row_size:(h+1)*48*row_size]+bytes(16*row_size) for h in range(4));(d/f'{kind}.bin').write_bytes(padded)
   (d/'mask.bin').write_bytes(struct.pack('<64e',*([0.0]*48+[-math.inf]*16)))
   a=Args();params={'ne01':1,'ne02':24,'ne03':1,'nb01':24576,'nb02':1024,'nb03':24576,'ne11':64,'ne_12_2':4,'ne_12_3':1,'ns10':8,'nb11':272,'nb12':64*272,'nb13':4*64*272,'ns20':2,'nb21':size,'nb22':64*size,'nb23':4*64*size,'ne31':1,'ne32':1,'ne33':1,'nb31':128,'nb32':128,'nb33':128,'ne1':256,'ne2':24,'ne3':1,'scale':.0625}
   for name,value in params.items():setattr(a,name,value)
   (d/'args.bin').write_bytes(bytes(a))
   shutil.copyfile(E/f'AW-0117/{layer}-{bits}/args.bin',d/'writer-args.bin')
   shutil.copyfile(E/f'AW-0117/{layer}-{bits}/input.bin',d/'values.bin')
   key=tensors[layer,1];keyvalues=[oracle.value(key,i,t,h) for h in range(4) for t in range(48) for i in range(256)]
   (d/'keys.bin').write_bytes(struct.pack('<49152f',*keyvalues))
   end=header.index('} ggml_metal_kargs_set_rows;');start=header.rfind('typedef struct {',0,end)
   keyfields=re.findall(r'(int32_t|uint64_t)\s+(\w+);',header[start:end])
   class WriterArgs(ctypes.Structure):_fields_=[(name,types[kind]) for kind,name in keyfields]
   keyargs=WriterArgs.from_buffer_copy((d/'writer-args.bin').read_bytes());keyargs.nk0=8;keyargs.nb1=272;keyargs.nb2=192*272;keyargs.nb3=192*272
   (d/'key-writer-args.bin').write_bytes(bytes(keyargs))
   (d/'indices.bin').write_bytes(struct.pack('<192q',*[h*64+t for h in range(4) for t in range(48)]))
 swift=Path('experiments/fixtures/turbo-kv-attention-chain.swift');binary=R/'dispatch';build_command=['swiftc','-O',str(swift),'-o',str(binary)];build=subprocess.run(build_command,capture_output=True,text=True);(R/'compile.log').write_text(build.stdout+build.stderr);assert build.returncode==0
 plan={'experiment':'AW-0119','harness_sha256':oracle.digest(__file__),'swift_sha256':oracle.digest(swift),'binary_sha256':oracle.digest(binary),'metal_sha256':oracle.digest(E/'AW-0115/embedded.metal'),'cpu_authority_sha256':oracle.digest(E/'AW-0113/result.json'),'capture_sha256':oracle.digest(E/'AW-0109/result.json'),'inputs':{str(p.relative_to(R)):oracle.digest(p) for p in R.glob('*/*.bin')},'args_size':ctypes.sizeof(Args),'args_fields':fields,'constants':{'has_mask':True,'has_sinks':False,'has_bias':False,'has_scap':False,'has_kvpad':False,'ns10':8,'ns20':2,'nsg':4,'nwg':1},'dispatch':[1,24,1],'threads':[32,4,1],'scratch_bytes':8192,'acceptance':'Six complete native writer-attention-inverse outputs finite and relative L2<=.005 versus AW113 CPU inverse aggregate; masked padded slots remain zero','timeout_seconds':90,'scope':'Connected native q8 key and Turbo value writers, compressed attention and inverse; real48-key FP16-generated trajectory; no Prism registration/accumulated compressed trajectory or endpoint performance'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');samples=[];error=None;start=time.monotonic()
 with (R/'dispatch.log').open('w') as log:
  proc=subprocess.Popen([str(binary),str(E/'AW-0115/embedded.metal'),str(R)],stdout=log,stderr=log,start_new_session=True)
  try:
   while proc.poll() is None:
    sample=host_sample();samples.append(sample);check_sample(sample,baseline[1])
    if time.monotonic()-start>90:raise RuntimeError('timeout')
    time.sleep(.25)
  except Exception as exc:error=str(exc)
  finally:
   if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 lib=ctypes.CDLL(str(E/'AW-0105/turbo-codec.dylib'));records=[]
 if proc.returncode==0 and not error:
  for bits in [3,4]:
   for layer in [3,31,63]:
    p=R/f'{layer}-{bits}/restored.bin';actual=struct.unpack('<6144f',p.read_bytes());refbuf=(ctypes.c_float*6144)(*struct.unpack('<6144f',(E/f'AW-0113/{layer}-turbo{bits}-aggregate.bin').read_bytes()));inverse=lib.turbo_cpu_fwht_inverse;inverse.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_int];inverse.restype=None
    for start in range(0,6144,128):inverse(ctypes.cast(ctypes.byref(refbuf,start*4),ctypes.POINTER(ctypes.c_float)),128)
    ref=list(refbuf);finite=all(math.isfinite(x) for x in actual);relative=math.sqrt(math.fsum((a-b)**2 for a,b in zip(actual,ref))/math.fsum(x*x for x in ref)) if finite else None
    records.append({'layer':layer,'bits':bits,'finite':finite,'relative_l2':relative,'passed':finite and relative<=.005,'output_sha256':oracle.digest(p)})
 result={'experiment':'AW-0119','exit':proc.returncode,'error':error,'passed':len(records)==6 and all(x['passed'] for x in records),'records':records,'pressure_peak':max(x[0] for x in samples),'swap_growth_peak_mib':max(0,max(x[1] for x in samples)-baseline[1]),'plan_sha256':oracle.digest(R/'plan.json'),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
