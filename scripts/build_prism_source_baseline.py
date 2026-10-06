#!/usr/bin/env python3
"""AW-0120 isolated pinned unmodified Prism runtime build before Turbo integration."""
import json,subprocess,time,os,signal,hashlib
from pathlib import Path
from run_local_agent import preflight,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0120');S=Path('/Users/chad/Models/agentwing/runtime-sources/prism-turbo');B=Path('/Users/chad/Models/agentwing/runtime-builds/prism-baseline');T=Path('/Users/chad/Models/agentwing/build-tools/bin')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 preflight();baseline=host_sample();R.mkdir(exist_ok=True)
 revision=subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD'],text=True).strip();assert revision=='adfffbe41b2cabcd51fff326ab045662265062bb';assert not subprocess.check_output(['git','-C',str(S),'status','--porcelain'],text=True).strip()
 commands=[[str(T/'cmake'),'-S',str(S),'-B',str(B),'-G','Ninja',f'-DCMAKE_MAKE_PROGRAM={T}/ninja','-DCMAKE_BUILD_TYPE=Release','-DGGML_METAL=ON','-DGGML_METAL_EMBED_LIBRARY=ON','-DLLAMA_BUILD_COMMON=OFF','-DLLAMA_BUILD_TESTS=OFF','-DLLAMA_BUILD_EXAMPLES=OFF','-DLLAMA_BUILD_TOOLS=OFF','-DLLAMA_BUILD_SERVER=OFF'],[str(T/'cmake'),'--build',str(B),'--target','llama','--parallel','2']]
 plan={'experiment':'AW-0120','source_revision':revision,'source_tree':subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD^{tree}'],text=True).strip(),'source_directory':str(S),'build_directory':str(B),'commands':commands,'harness_sha256':sha(__file__),'cmake_version':subprocess.check_output([str(T/'cmake'),'--version'],text=True),'ninja_version':subprocess.check_output([str(T/'ninja'),'--version'],text=True),'compiler':subprocess.check_output(['clang','--version'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'acceptance':'Both command exits0 and nonempty built runtime libraries; host pressure<4/swap growth<=1024MiB. Build only, no model runtime correctness/performance claim.','timeout_seconds_per_phase':600,'scope':'Isolated unmodified pinned Prism runtime baseline; existing launchers/control unchanged'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');records=[];samples=[];error=None
 for i,cmd in enumerate(commands):
  start=time.monotonic()
  with (R/f'phase-{i}.log').open('w') as log:
   proc=subprocess.Popen(cmd,stdout=log,stderr=log,start_new_session=True)
   try:
    while proc.poll() is None:
     sample=host_sample();samples.append(sample);check_sample(sample,baseline[1])
     with (R/'host.tsv').open('a') as f:f.write(f'{time.time()}\t{sample[0]}\t{sample[1]}\n')
     if time.monotonic()-start>600:raise RuntimeError('phase timeout')
     time.sleep(.5)
   except Exception as exc:error=str(exc)
   finally:
    if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  records.append({'phase':i,'exit':proc.returncode,'wall_seconds':time.monotonic()-start,'log_sha256':sha(R/f'phase-{i}.log')})
  if proc.returncode or error:break
 libraries={str(p.relative_to(B)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in B.rglob('*.dylib') if p.is_file()}
 result={'experiment':'AW-0120','passed':len(records)==2 and all(x['exit']==0 for x in records) and bool(libraries) and not error,'records':records,'error':error,'libraries':libraries,'pressure_peak':max(x[0] for x in samples),'swap_growth_peak_mib':max(0,max(x[1] for x in samples)-baseline[1]),'plan_sha256':sha(R/'plan.json'),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
