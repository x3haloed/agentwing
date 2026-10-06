#!/usr/bin/env python3
"""AW-0132 integrated Prism Metal SET_ROWS graph fidelity on real rows."""
import json,subprocess,hashlib,time,os,signal,shutil,ctypes
from pathlib import Path
from run_local_agent import preflight,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0132');E=R.parent;S=Path('/Users/chad/Models/agentwing/runtime-sources/prism-turbo-port');B=Path('/Users/chad/Models/agentwing/runtime-builds/prism-turbo-inverse/bin')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 preflight();baseline=host_sample();R.mkdir(exist_ok=True);authority=json.loads((E/'AW-0131/result.json').read_text());assert authority['passed']
 source=Path('experiments/fixtures/prism-turbo-attention-inverse.cpp');binary=R/'set-rows';command=['clang++','-std=c++17','-O2','-I'+str(S/'ggml/include'),str(source),'-L'+str(B),'-lggml','-lggml-base','-lggml-metal','-lggml-cpu','-Wl,-rpath,'+str(B),'-o',str(binary)];build=subprocess.run(command,capture_output=True,text=True);(R/'compile.log').write_text(build.stdout+build.stderr);assert build.returncode==0
 plan={'experiment':'AW-0132','source_sha256':sha(source),'harness_sha256':sha(__file__),'binary_sha256':sha(binary),'build_authority_sha256':sha(E/'AW-0131/result.json'),'libraries':{p.name:sha(p) for p in B.glob('*.dylib')},'input_authority_sha256':sha(E/'AW-0116/result.json'),'cpu_authority_sha256':sha(E/'AW-0113/result.json'),'command':command,'acceptance':'Each actual Prism flash attention graph reports supported, exits0, finite full outputs and relative L2<=.005 versus AW113 compressed CPU inverse aggregate; CPU backend must explicitly deny inverse operation','timeout_seconds_per_case':90,'scope':'Integrated Prism Metal asymmetric attention plus inverse graph; CPU denies unsupported inverse; no model-cache graph or compressed generation/endpoint qualification'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');records=[];samples=[]
 for bits in [3,4]:
  for layer in [3,31,63]:
   p=E/f'AW-0116/{layer}-{bits}';target=R/f'{layer}-{bits}.bin';error=None;start=time.monotonic()
   with (R/f'{layer}-{bits}.log').open('w') as log:
    proc=subprocess.Popen([str(binary),str(bits),str(p),str(target),'AW0126'],stdout=log,stderr=log,start_new_session=True)
    try:
     while proc.poll() is None:
      sample=host_sample();samples.append(sample);check_sample(sample,baseline[1])
      with (R/'host.tsv').open('a') as f:f.write(f'{time.time()}\t{sample[0]}\t{sample[1]}\n')
      if time.monotonic()-start>90:raise RuntimeError('timeout')
      time.sleep(.25)
    except Exception as exc:error=str(exc)
    finally:
     if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   reference=(E/f'AW-0113/{layer}-turbo{bits}-aggregate.bin').read_bytes();same=False;relative=None
   import struct
   lib=ctypes.CDLL(str(B/'libggml-base.0.21.0.dylib'));inverse=lib.turbo_cpu_fwht_inverse;inverse.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_int];inverse.restype=None;values=(ctypes.c_float*6144)(*struct.unpack('<6144f',reference))
   for start in range(0,6144,128):inverse(ctypes.cast(ctypes.byref(values,start*4),ctypes.POINTER(ctypes.c_float)),128)
   reference=bytes(values)
   if target.exists():
    import math,struct
    actual=struct.unpack('<6144f',target.read_bytes());ref=struct.unpack('<6144f',reference);relative=math.sqrt(math.fsum((a-b)**2 for a,b in zip(actual,ref))/math.fsum(x*x for x in ref)) if all(math.isfinite(x) for x in actual) else None;same=relative is not None and relative<=.005
   records.append({'bits':bits,'layer':layer,'exit':proc.returncode,'error':error,'relative_l2':relative,'passes_cpu_authority_limit':same,'passed':proc.returncode==0 and not error and same,'output_sha256':sha(target) if target.exists() else None})
   if proc.returncode or error:break
  if proc.returncode or error:break
 result={'experiment':'AW-0132','passed':len(records)==6 and all(x['passed'] for x in records),'records':records,'pressure_peak':max(x[0] for x in samples),'swap_growth_peak_mib':max(0,max(x[1] for x in samples)-baseline[1]),'plan_sha256':sha(R/'plan.json'),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
