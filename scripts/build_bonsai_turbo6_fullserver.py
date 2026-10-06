#!/usr/bin/env python3
"""AW210 pinned Turbo6 server/vision build, without model admission."""
import json,subprocess,time,shutil
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group
R=Path('/Users/chad/Models/agentwing/evidence/AW-0210');B=Path('/Users/chad/Models/agentwing/runtime-builds/prism-turbo6');S=Path('/Users/chad/Models/agentwing/runtime-sources/prism-turbo6');T=Path('/Users/chad/Models/agentwing/build-tools/bin/cmake')
def main():
 preflight();assert not (R/'plan.json').exists();parent=json.loads((ROOT/'evidence/AW-0209-turbo6-cache-terminal.json').read_text());assert parent['terminal_audit']['passed'];baseline=host_sample();commands=[[str(T),'--build',str(B),'--target','llama-server','llama-mtmd-cli','-j4']]
 for name,h in parent['plan']['candidate_build']['libraries_sha256'].items():assert digest(B/'bin'/name)==h
 plan={'experiment':'AW-0210','hypothesis':'Existing native6bit survivor builds complete server/vision executables without source or priorlibrary drift','acceptance':'buildexit0/nonemptyserverandvisionCLI, priornativecodec/model librariesunchanged, sourcehashesunchanged, pressure<4/swapgrowth<=1024MiB/freeSSD>=8GiB/600sphase','commands':commands,'parent_receipt_sha256':digest(ROOT/'evidence/AW-0209-turbo6-cache-terminal.json'),'source_sha256':parent['source_reconstruction']['changed_sources_sha256'],'prior_libraries_sha256':parent['plan']['candidate_build']['libraries_sha256'],'runner_sha256':digest(Path(__file__)),'storage_recovery_sha256':digest(R/'storage-recovery.json'),'compiler':subprocess.check_output(['clang++','--version'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.run(['pmset','-g','therm'],capture_output=True,text=True).stdout,'storage':'internalSSD','scope':'Serverandvision build only, no model startup/inference/tool/endpoint qualification'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');start=time.monotonic();error=None
 with (R/'build.log').open('w') as log:
  p=subprocess.Popen(commands[0],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   while p.poll() is None:
    h=host_sample();free=shutil.disk_usage(R).free;check_sample(h,baseline[1]);assert free>=8*1024**3
    with (R/'host.jsonl').open('a') as f:f.write(json.dumps({'time':time.time(),'pressure':h[0],'swap_mib':h[1],'free_bytes':free})+'\n')
    if time.monotonic()-start>600:raise RuntimeError('buildtimeout')
    time.sleep(.5)
  except Exception as exc:error=str(exc)
  finally:stop_group(p)
 binaries={name:digest(B/'bin'/name) for name in ['llama-server','llama-mtmd-cli'] if (B/'bin'/name).exists()};libraries={p.name:digest(p) for p in (B/'bin').glob('*.dylib')};prior_unchanged=all(libraries[n]==h for n,h in plan['prior_libraries_sha256'].items());source_unchanged=all(digest(S/n)==h for n,h in plan['source_sha256'].items());version=subprocess.check_output([str(B/'bin/llama-server'),'--version'],stderr=subprocess.STDOUT,text=True) if p.returncode==0 else None
 result={'experiment':'AW-0210','passed':p.returncode==0 and not error and len(binaries)==2 and prior_unchanged and source_unchanged,'exit':p.returncode,'error':error,'build_wall_seconds':time.monotonic()-start,'binaries_sha256':binaries,'libraries_sha256':libraries,'prior_libraries_unchanged':prior_unchanged,'changed_sources_unchanged':source_unchanged,'version_output':version,'plan_sha256':digest(R/'plan.json'),'raw_sha256':{p.name:digest(p) for p in R.iterdir() if p.is_file()},'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
