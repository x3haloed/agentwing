#!/usr/bin/env python3
"""AW226 matched sequential state diagnostic, no performance qualification."""
import fcntl,hashlib,json,shutil,struct,subprocess,time
from pathlib import Path
from run_local_agent import ROOT,preflight,host_sample,check_sample,stop_group
from bonsai_turbo6_server import verify
R=Path('/Users/chad/Models/agentwing/evidence/AW-0226');S=Path('/Users/chad/Models/agentwing/runtime-sources/prism-gen-checkpoints-full');B=Path('/Users/chad/Models/agentwing/runtime-builds/prism-gen-checkpoints-full/bin');I=Path('/Users/chad/Models/agentwing/evidence/AW-0223/cheap-restore')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 preflight();assert not R.exists();assert shutil.disk_usage(R.parent).free>=16*1024**3;verify()
 pins=json.loads((ROOT/'evidence/AW-0223-isolated-build.json').read_text())
 for n,h in pins['artifacts_sha256'].items():assert sha(B/n)==h
 R.mkdir(mode=0o700)
 prefix=json.loads((I/'tokenize-response.json').read_text())['tokens'];generated=json.loads((I/'generate-response.json').read_text())['tokens'];tokens=prefix+(generated*3)[:1715];assert len(tokens)==1735
 (R/'tokens.i32').write_bytes(struct.pack('<1735i',*tokens))
 fixture=ROOT/'experiments/fixtures/bonsai-checkpoint-boundaries.cpp'
 cmd=['clang++','-std=c++17','-O2','-I'+str(S/'include'),'-I'+str(S/'ggml/include'),str(fixture),'-L'+str(B),'-lllama','-lggml','-lggml-base','-Wl,-rpath,'+str(B),'-o',str(R/'state-screen')]
 plan={'experiment':'AW-0226','scope':'Seven boundary cases, synthetic extension of owned generated tokens, native correctness only; no server-hook/fullcost/task qualification','build_command':cmd,'fixture_sha256':sha(fixture),'runner_sha256':sha(Path(__file__)),'input_sha256':sha(R/'tokens.i32'),'input_parent_receipt_sha256':sha(ROOT/'evidence/AW-0223-cheap-restore-terminal.json'),'runtime_build_sha256':sha(ROOT/'evidence/AW-0223-isolated-build.json'),'model':'selectiveBonsai/Q8K/Turbo6V','context':16384,'n_rs_seq':0,'path':'Sequential1735 history, checkpoints531/1043/1555 boundedring2. Targets1042/1043/1044/1554/1555/1556/1594; latestcheckpoint strictlybeforetarget, fallbackfirst20+sequential if unavailable. Independent cases resetfullKV fromsavedstate; matchedcontrol arithmetic.','acceptance':'Finite248320logits,maxabs<=1e-5,relativeL2<=1e-6,sameargmax. Stateget/set/remove must succeed. Pressure<4/swapgrowth<=1024MiB/disk>=8GiB/1800s. No waiver of AW2230.01failure.','os':subprocess.check_output(['sw_vers'],text=True),'thermal':subprocess.run(['pmset','-g','therm'],capture_output=True,text=True).stdout,'storage':'internalSSD, warm OS cache uncontrolled'}
 (R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 with (R/'build.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=f,check=True)
 baseline=host_sample()[1];start=time.monotonic();error=None
 with (ROOT/'var/model-owner.lock').open('a') as lock,(R/'native.log').open('w') as err,(R/'capture.txt').open('w') as out:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  proc=subprocess.Popen([str(R/'state-screen'),'/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-attention-PQ2_0.gguf',str(R/'tokens.i32'),str(R),str(B)],stdout=out,stderr=err,start_new_session=True)
  try:
   while proc.poll() is None:
    p,s=host_sample();check_sample((p,s),baseline);free=shutil.disk_usage(R).free
    with (R/'host.jsonl').open('a') as f:f.write(json.dumps({'time':time.time(),'pressure':p,'swap_mib':s,'free_bytes':free})+'\n')
    if free<8*1024**3:raise RuntimeError('disk-gate')
    if time.monotonic()-start>1800:raise RuntimeError('timeout')
    time.sleep(.5)
  except BaseException as exc:error=str(exc)
  finally:stop_group(proc)
 result={'exit':proc.returncode,'error':error,'wall_seconds_diagnostic':time.monotonic()-start,'numeric_audit_pending':True}
 (R/'result.json').write_text(json.dumps(result,indent=2)+'\n');(R/'hashes.json').write_text(json.dumps({p.name:sha(p) for p in R.iterdir() if p.is_file()},indent=2)+'\n');print(json.dumps(result))
 if error or proc.returncode:raise SystemExit(1)
if __name__=='__main__':main()
