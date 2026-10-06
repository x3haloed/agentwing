#!/usr/bin/env python3
"""AW-0111 unchanged upstream Metal WHT versus independent CPU real rows."""
import ctypes,json,math,re,struct,subprocess,shutil
from pathlib import Path
import check_bonsai_attention_oracle as oracle
from run_local_agent import preflight,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0111')
SOURCE=Path('/Volumes/Elements/mimo-prismwing/research-sources/atomic-llama-cpp-turboquant/ggml/src/ggml-metal')
def main():
 preflight();baseline=host_sample();R.mkdir(exist_ok=True)
 metal=(SOURCE/'ggml-metal.metal').read_text();header=(SOURCE/'ggml-metal-impl.h').read_text()
 signs=metal[metal.index('constant half4 turbo_wht_signs1_h4'):metal.index('// --- QJL sign arrays ---')]
 kernel=metal[metal.index('kernel void kernel_turbo_wht('):metal.index('constant short FC_solve_tri_nsg')]
 decl=re.search(r'typedef struct \{\s*int64_t\s+n_elements;[^}]+\} ggml_metal_kargs_turbo_wht;',header).group()
 extracted='#include <metal_stdlib>\nusing namespace metal;\n'+decl+'\n'+signs+'\n'+kernel
 (R/'extracted.metal').write_text(extracted)
 swift=Path('experiments/fixtures/turbo-wht-metal.swift');binary=R/'wht-metal'
 compile_command=['swiftc','-O',str(swift),'-o',str(binary)]
 compilation=subprocess.run(compile_command,capture_output=True,text=True);(R/'compile.log').write_text(compilation.stdout+compilation.stderr);assert compilation.returncode==0
 libpath=R.parent/'AW-0105/turbo-codec.dylib';lib=ctypes.CDLL(str(libpath))
 plan={'experiment':'AW-0111','source_sha256':oracle.digest(SOURCE/'ggml-metal.metal'),'header_sha256':oracle.digest(SOURCE/'ggml-metal-impl.h'),'extracted_sha256':oracle.digest(R/'extracted.metal'),'harness_sha256':oracle.digest(__file__),'swift_sha256':oracle.digest(swift),'binary_sha256':oracle.digest(binary),'codec_sha256':oracle.digest(libpath),'capture_sha256':oracle.digest(R.parent/'AW-0109/result.json'),'compile_command':compile_command,'relative_l2_limit':0.005,'acceptance':'Unchanged upstream Metal128-group forward/inverse WHT finite and relative L2<=.005 versus CPU on every real populated Q/V row collection. Half butterfly precision allowed; no model quality acceptance.','scope':'Metal transform only; no compressed attention dispatch, model-cache integration, speed or endpoint claim'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 oracle.CAPTURE=R.parent/'AW-0109';tensors=oracle.read_capture();records=[]
 for layer in [3,31,63]:
  for role,nt,nh in [(0,1,24),(2,48,4)]:
   t=tensors[layer,role];values=[oracle.value(t,d,token,head) for head in range(nh) for token in range(nt) for d in range(256)]
   assert all(math.isfinite(x) for x in values);p=R/f'{layer}-{role}-input.bin';p.write_bytes(struct.pack('<'+'f'*len(values),*values))
   for direction,name in [(0,'forward'),(1,'inverse')]:
    fn=getattr(lib,'turbo_cpu_fwht_'+name);fn.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_int];fn.restype=None;out=(ctypes.c_float*len(values))(*values)
    for start in range(0,len(values),128):fn(ctypes.cast(ctypes.byref(out,start*4),ctypes.POINTER(ctypes.c_float)),128)
    target=R/f'{layer}-{role}-{name}.bin';command=[str(binary),str(R/'extracted.metal'),str(p),str(target),str(direction)]
    run=subprocess.run(command,capture_output=True,text=True,timeout=60);assert run.returncode==0,(run.stdout,run.stderr)
    actual=struct.unpack('<'+'f'*len(values),target.read_bytes());assert all(math.isfinite(x) for x in actual)
    relative=math.sqrt(math.fsum((a-b)**2 for a,b in zip(actual,out))/math.fsum(x*x for x in out))
    records.append({'layer':layer,'role':role,'direction':name,'values':len(values),'relative_l2':relative,'passed':relative<=.005,'device':run.stdout.strip(),'output_sha256':oracle.digest(target)})
    check_sample(host_sample(),baseline[1])
 result={'experiment':'AW-0111','passed':all(x['passed'] for x in records) and len(records)==12,'records':records,'plan_sha256':oracle.digest(R/'plan.json'),'phase_host_samples':[baseline,host_sample()],'os':subprocess.check_output(['sw_vers'],text=True),'scope':plan['scope']}
 (R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
