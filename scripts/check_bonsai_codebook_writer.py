#!/usr/bin/env python3
"""AW187 same-layout real Metal writer numeric/cost ABBA screen."""
import fcntl,json,subprocess,time,re,statistics
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group
R=Path('/Users/chad/Models/agentwing/evidence/AW-0187');I=R.parent/'AW-0185'
def main():
 assert not (R/'plan.json').exists();preflight();authority=json.loads((ROOT/'evidence/AW-0185-actual-codebook-screen.json').read_text());assert authority['result']['passed'];builds={a:json.loads((ROOT/n).read_text()) for a,n in [('control','evidence/AW-0182-mixed-cache-graph-init.json'),('candidate','evidence/AW-0186-stationary-codebook-build.json')]};builds['control']=builds['control']['build']
 for arm,b in builds.items():
  for name,h in b['libraries_sha256'].items():assert digest(Path(b['build_directory'])/'bin'/name)==h
 plan={'experiment':'AW-0187','hypothesis':'Stationary table Metal writer retains packed/index integrity without material construction-cost regression','acceptance':'All nibble codes match own CPU reference after reverse192row placement; reserved2byteszero; finite FP16 normrelative<=.0015;12cases exit0/hostgates;5compute/readback windows each. Predeclared cost screen each adjacent candidate/control steady median ratio<=1.10, uncertainty retained; no endpoint promotion','source_sha256':digest(ROOT/'experiments/fixtures/bonsai-codebook-writer.cpp'),'runner_sha256':digest(Path(__file__)),'binaries_sha256':{a:digest(R/a) for a in builds},'builds':builds,'input_authority_sha256':digest(ROOT/'evidence/AW-0185-actual-codebook-screen.json'),'inputs_sha256':{p.name:digest(p) for p in I.glob('*.bin')},'order':[(l,a) for l in [3,31,63] for a in ['control','candidate','candidate','control']],'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'internalSSD','cache':'Fresh process per arm; uncontrolled warm OS cache; ABBA per layer; first warmup retained','scope':'Actual192row V cache writer primitive; setup/compile/uploads retained in lifetime separately; not full writer-attention or endpoint timing'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');rows=[]
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for index,(layer,arm) in enumerate(plan['order']):
   preflight();baseline=host_sample()[1];samples=[];error=None;proc=None;out=R/f'{index}-{arm}.bin';logpath=R/f'{index}-{arm}.log';start=time.monotonic()
   with logpath.open('w') as log:
    try:
     proc=subprocess.Popen([str(R/arm),'4',str(I/f'{layer}-input.bin'),str(out),'AW187'],stdout=log,stderr=log,start_new_session=True)
     while proc.poll() is None:
      s=host_sample();samples.append(s);check_sample(s,baseline)
      if time.monotonic()-start>90:raise RuntimeError('timeout')
      time.sleep(.25)
    except Exception as exc:error=str(exc)
    finally:stop_group(proc)
   timings=[float(v) for v in re.findall(r'compute_readback_seconds=([\d.]+)',logpath.read_text())];parity=False;scale_error=None
   if out.exists():
    actual=np.frombuffer(out.read_bytes(),dtype=np.uint8).reshape(192,136)[::-1].copy().reshape(384,68);kind='native' if arm=='control' else 'candidate';ref=np.frombuffer((I/f'{layer}-{kind}-packed.bin').read_bytes(),dtype=np.uint8).reshape(384,68);a=actual[:,:2].copy().view('<f2').reshape(-1).astype(float);b=ref[:,:2].copy().view('<f2').reshape(-1).astype(float);scale_error=float(np.max(np.abs(a-b)/np.maximum(np.abs(b),1e-30)));parity=bool(np.array_equal(actual[:,4:],ref[:,4:]) and not actual[:,2:4].any() and np.isfinite(a).all() and scale_error<=.0015)
   row={'index':index,'layer':layer,'arm':arm,'exit':proc.returncode if proc else None,'error':error,'packed_index_scale_gate_passed':parity,'max_norm_relative_error':scale_error,'all_iteration_seconds':timings,'steady_median_seconds':statistics.median(timings[1:]) if len(timings)==5 else None,'pressure_peak':max((s[0] for s in samples),default=None),'baseline_swap_mib':baseline,'swap_growth_peak_mib':max((max(0,s[1]-baseline) for s in samples),default=None),'lifetime_seconds':time.monotonic()-start,'output_sha256':digest(out) if out.exists() else None,'log_sha256':digest(logpath)};rows.append(row);(R/f'{index}-result.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
   if error or proc.returncode or not parity or len(timings)!=5:break
 pairs=[{'layer':rows[i]['layer'],'ratio':rows[i+1]['steady_median_seconds']/rows[i]['steady_median_seconds']} for i in range(0,len(rows),4) if i+3<len(rows)]+[{'layer':rows[i]['layer'],'ratio':rows[i+2]['steady_median_seconds']/rows[i+3]['steady_median_seconds']} for i in range(0,len(rows),4) if i+3<len(rows)]
 result={'experiment':'AW-0187','complete':len(rows)==12,'numeric_passed':len(rows)==12 and all(x['packed_index_scale_gate_passed'] and x['exit']==0 and not x['error'] for x in rows),'cost_gate_passed':len(pairs)==6 and all(x['ratio']<=1.10 for x in pairs),'rows':rows,'pairs':pairs,'unattempted':plan['order'][len(rows):],'plan_sha256':digest(R/'plan.json'),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
