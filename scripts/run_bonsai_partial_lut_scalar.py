#!/usr/bin/env python3
"""AW173 guarded ABBA full-matrix candidate construction/application screen."""
import fcntl,json,re,statistics,subprocess,time
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group
from bonsai_turbo_server import verify,SPEC

def main():
 r=Path('/Users/chad/Models/agentwing/evidence/AW-0173');base=Path('/Users/chad/Models/agentwing/evidence/AW-0167')
 plan=json.loads((r/'plan.json').read_text());assert not (r/'summary.json').exists()
 for p,h in plan['sources_sha256'].items():assert digest(ROOT/p)==h
 for p,h in plan['fixture_sha256'].items():assert digest(base/p)==h
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);preflight();verify()
  metadata={'plan_sha256':digest(r/'plan.json'),'runner_sha256':digest(Path(__file__)),'candidate_binary_sha256':digest(r/'candidate'),'parent_runtime_profile':json.loads(SPEC.read_text()),'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'Internal SSD','cache':'Warm uncontrolled OS cache; fresh process per arm, first iteration retained warmup. ABBA; not endpoint comparison.'}
  (r/'execution-plan.json').write_text(json.dumps(metadata,indent=2)+'\n');rows=[];reference=np.fromfile(base/'control-output.bin',dtype='<f4').astype(np.float64)
  for i,arm in enumerate(plan['order']):
   preflight();out=r/f'{i}-{arm}.bin'
   cmd=([str(base/'control'),str(base/'weights.bin'),str(base/'input.bin'),str(out),'17408','5120'] if arm=='control' else [str(r/'candidate'),str(ROOT/'experiments/fixtures/bonsai-partial-lut-scalar.metal'),str(base/'weights.bin'),str(base/'input.bin'),str(out),'17408','5120'])
   baseline=host_sample()[1];samples=[];child=None;error=None;start=time.monotonic()
   with (r/f'{i}-{arm}.log').open('w') as log:
    try:
     child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
     while child.poll() is None:
      s=host_sample();samples.append(s);check_sample(s,baseline)
      if time.monotonic()-start>60:raise RuntimeError('watchdog')
      time.sleep(.1)
     if child.returncode:raise RuntimeError('fixture-exit-'+str(child.returncode))
    except Exception as exc:error=str(exc)
    finally:stop_group(child)
   timings=[float(x) for x in re.findall(r'(?:compute_and_readback|build_multiply_readback)_seconds=([\d.]+)',(r/f'{i}-{arm}.log').read_text())]
   relative=None;numeric=False
   if out.exists():
    v=np.fromfile(out,dtype='<f4').astype(np.float64)
    if v.shape==reference.shape and np.isfinite(v).all():relative=float(np.linalg.norm(v-reference)/np.linalg.norm(reference));numeric=relative<=.0001
   row={'arm':arm,'index':i,'command':cmd,'error':error,'exit':child.returncode if child else None,'numeric_passed':numeric,'relative_L2':relative,'all_iteration_seconds':timings,'steady_median_seconds':statistics.median(timings[1:]) if len(timings)==5 else None,'fixture_lifetime_seconds':time.monotonic()-start,'pressure_peak':max((s[0] for s in samples),default=None),'baseline_swap_mib':baseline,'swap_growth_peak_mib':max((max(0,s[1]-baseline) for s in samples),default=None),'output_sha256':digest(out) if out.exists() else None,'log_sha256':digest(r/f'{i}-{arm}.log')}
   rows.append(row);(r/f'{i}-result.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
   if error or not numeric or len(timings)!=5:break
  summary={'experiment':'AW-0173','complete':len(rows)==4,'rows':rows,'scope':plan['scope'],'unattempted':plan['order'][len(rows):],'raw_sha256':{p.name:digest(p) for p in r.iterdir() if p.is_file()}}
  (r/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
  if len(rows)!=4 or any(x['error'] or not x['numeric_passed'] for x in rows):raise SystemExit(1)

if __name__=='__main__':main()
