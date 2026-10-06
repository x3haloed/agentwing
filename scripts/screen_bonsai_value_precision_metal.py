#!/usr/bin/env python3
"""AW200 isolated Metal encode/decode implementation screen, not llama runtime."""
import json,subprocess,time,shutil
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,digest,preflight,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0200');P=R.parent/'AW-0199'
def main():
 preflight();R.mkdir(exist_ok=False);base=host_sample();parent=json.loads((P/'result.json').read_text());assert parent['passed']
 binary=P/'precision-metal';shader=ROOT/'experiments/fixtures/bonsai-precision-metal.metal'
 plan={'experiment':'AW-0200','hypothesis':'Isolated M1 Metal6bit encode/decode preserves AW199 indices, norm scale and inverse numerical result on all3actual layers','acceptance':'All packed code indices equal CPU; half norm scale differs <=0.2%; full decoded relativeL2 against CPU <=0.005; finite; pressure<4, swapgrowth<=1024MiB, diskfree>=8GiB','primary_metric':'correctness across actual early/mid/late fixtures; cost recorded only, no runtime cost acceptance or speed claim','order':[4,6,6,4],'windows':5,'repeats':64,'parent_result_sha256':digest(P/'result.json'),'binary_sha256':digest(binary),'shader_sha256':digest(shader),'host_source_sha256':digest(ROOT/'experiments/fixtures/bonsai-precision-metal.mm'),'runner_sha256':digest(Path(__file__)),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),'thermal':subprocess.run(['pmset','-g','therm'],text=True,capture_output=True).stdout,'storage':'internalSSD','sampling_context_tasks':'not applicable: saved components, no inference/tool execution','scope':'Standalone Metal prototypes with binary-search tables and float inverse; not native llama SET_ROWS or flash attention; no model, vision, behavior or endpoint evidence'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');rows=[]
 for bits in [4,6]:
  t=parent['tables'][str(bits)];(R/f'book-{bits}.bin').write_bytes(np.array(t['centroids']+t['thresholds'],dtype='<f4').tobytes())
 for layer in [3,31,63]:
  for slot,bits in enumerate(plan['order']):
   d=R/f'{layer}-{slot}-{bits}';d.mkdir();cmd=[str(binary),str(shader),str(bits),str(R.parent/'AW-0185'/f'{layer}-input.bin'),str(R/f'book-{bits}.bin'),str(d/'packed.bin'),str(d/'decoded.bin')];(d/'command.json').write_text(json.dumps(cmd)+'\n');samples=[]
   with (d/'log.txt').open('w') as log:
    start=time.monotonic();p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
    try:
     while p.poll() is None:
      h=host_sample();free=shutil.disk_usage(R).free;samples.append({'monotonic':time.monotonic(),'pressure':h[0],'swap_mib':h[1],'free_bytes':free});check_sample(h,base[1]);assert free>=8*1024**3;time.sleep(.5)
     assert p.returncode==0
    finally:
     if p.poll() is None:p.kill();p.wait()
     (d/'host.json').write_text(json.dumps(samples,indent=2)+'\n')
   size=4+16*bits;a=(d/'packed.bin').read_bytes();b=(P/f'{layer}-{bits}-packed.bin').read_bytes();assert len(a)==len(b)==384*size
   scale_error=0
   for group in range(384):
    x=a[group*size:(group+1)*size];y=b[group*size:(group+1)*size];assert x[2:]==y[2:],'Packed code indices/reserved fields differ';s=float(np.frombuffer(x[:2],dtype='<f2')[0]);ref=float(np.frombuffer(y[:2],dtype='<f2')[0]);scale_error=max(scale_error,abs(s-ref)/max(abs(ref),1e-10))
   decoded=np.fromfile(d/'decoded.bin',dtype='<f4').astype(float);cpu=np.fromfile(P/f'{layer}-{bits}-decoded.bin',dtype='<f4').astype(float);assert np.isfinite(decoded).all();error=float(np.linalg.norm(decoded-cpu)/np.linalg.norm(cpu));assert scale_error<=.002 and error<=.005
   rows.append({'layer':layer,'slot':slot,'bits':bits,'decoded_relative_l2':error,'scale_max_relative_error':scale_error,'process_seconds_diagnostic':time.monotonic()-start,'exit_code':p.returncode})
 result={'experiment':'AW-0200','passed':True,'records':rows,'plan_sha256':digest(R/'plan.json'),'raw_sha256':{str(p.relative_to(R)):digest(p) for p in R.rglob('*') if p.is_file()},'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
