#!/usr/bin/env python3
"""AW204 math-mode diagnostic on saved native writer mismatch."""
import json,subprocess,time,shutil
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,digest,preflight,host_sample,check_sample,stop_group
R=Path('/Users/chad/Models/agentwing/evidence/AW-0204');P=R.parent/'AW-0199'
def codes(raw,bits):
 size=4+16*bits
 return np.array([[(int.from_bytes(row[4:],'little')>>(i*bits))&((1<<bits)-1) for i in range(128)] for row in [raw[b*size:(b+1)*size] for b in range(384)]])
def main():
 preflight();assert not (R/'plan.json').exists();base=host_sample();native=np.fromfile(R.parent/'AW-0203/attempt-1/1-candidate.bin',dtype=np.uint8).reshape(192,200)[::-1].copy().tobytes()
 plan={'experiment':'AW-0204','hypothesis':'Explicit fast versus precise Metal compilation reproduces or removes AW203 single-bin mismatch on unchanged early-layer fixture','acceptance':'Both modes exit0/finite outputs/hostgates; diagnostic comparisons disclose whether entire native payload is reproduced; causal attribution to native compiler remains conditional because standalone scheduling/source differs','order':[(4,0),(6,1),(6,0),(4,1)],'scope':'Standalone mode-toggle diagnostic with rotated coordinate capture; not native writer repair or admission, no performance claim','source_sha256':digest(ROOT/'experiments/fixtures/bonsai-precision-mode.metal'),'host_source_sha256':digest(ROOT/'experiments/fixtures/bonsai-precision-mode.mm'),'binary_sha256':digest(R/'mode-probe'),'runner_sha256':digest(Path(__file__)),'native_receipt_sha256':digest(ROOT/'evidence/AW-0203-turbo6-native-writer-terminal.json'),'input_sha256':digest(R.parent/'AW-0185/3-input.bin'),'native_packed_sha256':digest(R.parent/'AW-0203/attempt-1/1-candidate.bin'),'parent_result_sha256':digest(P/'result.json'),'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.run(['pmset','-g','therm'],capture_output=True,text=True).stdout,'storage':'internalSSD','sampling_context_tools':'not applicable, no inference/tools'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');rows=[]
 for bits,fast in plan['order']:
  d=R/f'{bits}-{fast}';d.mkdir();cmd=[str(R/'mode-probe'),str(ROOT/'experiments/fixtures/bonsai-precision-mode.metal'),str(bits),str(R.parent/'AW-0185/3-input.bin'),str(R.parent/'AW-0200'/f'book-{bits}.bin'),str(d/'packed.bin'),str(d/'decoded.bin'),str(fast),str(d/'rotated.bin')];(d/'command.json').write_text(json.dumps(cmd)+'\n');samples=[]
  with (d/'log.txt').open('w') as log:
   proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   try:
    while proc.poll() is None:
     h=host_sample();check_sample(h,base[1]);free=shutil.disk_usage(R).free;assert free>=8*1024**3;samples.append({'pressure':h[0],'swap_mib':h[1],'free_bytes':free,'time':time.time()});time.sleep(.25)
    assert proc.returncode==0
   finally:stop_group(proc);(d/'host.json').write_text(json.dumps(samples,indent=2)+'\n')
  packed=(d/'packed.bin').read_bytes();cpu=(P/f'3-{bits}-packed.bin').read_bytes();a=codes(packed,bits);b=codes(cpu,bits);rot=np.fromfile(d/'rotated.bin',dtype='<f4').reshape(384,128);assert np.isfinite(rot).all();decoded=np.fromfile(d/'decoded.bin',dtype='<f4');assert np.isfinite(decoded).all();row={'bits':bits,'fast_math':fast,'cpu_mismatched_codes':int(np.count_nonzero(a!=b)),'cpu_packed_byteexact':packed==cpu,'captured_rotated_coordinate_148_29':float(rot[148,29]),'exit':proc.returncode}
  if bits==6:row.update(native_mismatched_codes=int(np.count_nonzero(a!=codes(native,6))),native_packed_byteexact=packed==native)
  rows.append(row)
 result={'experiment':'AW-0204','records':rows,'plan_sha256':digest(R/'plan.json'),'raw_sha256':{str(p.relative_to(R)):digest(p) for p in R.rglob('*') if p.is_file()},'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
