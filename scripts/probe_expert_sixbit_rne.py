#!/usr/bin/env python3
"""AW-0057 supervised original-kernel reference on admitted real activations."""
import datetime
import fcntl
import json
from pathlib import Path
import signal
import subprocess
import time
from run_local_agent import ROOT, preflight, host_sample, check_sample, stop_group, digest
from probe_expert_residency import MODEL


def main():
    with (ROOT/'var/local-agent.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);preflight()
        root=Path('/Users/chad/Models/agentwing/evidence/AW-0057');root.mkdir(exist_ok=True)
        run=root/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(mode=0o700);(run/'stages').mkdir()
        prior=Path('/Users/chad/Models/agentwing/evidence/AW-0036/20260906T062421.091973Z')
        receipt=json.loads((prior/'sha256.json').read_text())
        for rel,h in receipt.items():assert digest(prior/rel)==h,rel
        summary=json.loads((prior/'summary.json').read_text());assert summary['all_outputs_match'] and all(summary['route_equivalence'].values())
        fixtures=[]
        for case in ['coding','arithmetic','structured']:
            fixtures += [dict(json.loads(s),case=case) for s in (prior/(case+'-A1')/'activations.jsonl').read_text().splitlines()]
        assert len(fixtures)==72
        (run/'fixtures.json').write_text(json.dumps(fixtures)+'\n')
        source=ROOT/'probes/expert_sixbit_rne.m';(run/'expert_sixbit_rne.m').write_bytes(source.read_bytes());(run/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
        kernels=Path('/Users/chad/Models/agentwing/dependencies/Swiftlet/Sources/SwiftletCore/Kernels.metal.txt');(run/'Kernels.metal.txt').write_bytes(kernels.read_bytes())
        binary=run/'expert_sixbit_rne';build=['xcrun','clang','-O2','-fobjc-arc','-framework','Foundation','-framework','Metal',str(source),'-o',str(binary)]
        with (run/'build.log').open('w') as log:
            built=subprocess.run(build,stdout=log,stderr=subprocess.STDOUT)
        print(run,flush=True)
        if built.returncode:raise RuntimeError('Native reference build failed; see preserved build.log')
        manifest={'build':build,'source_sha256':digest(source),'binary_sha256':digest(binary),'kernel_sha256':digest(kernels),'activation_receipt_sha256':digest(prior/'sha256.json'),'model':MODEL,'layout_sha256':digest(Path(MODEL)/'packed_experts/layout.json'),'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal_before':subprocess.check_output(['pmset','-g','therm'],text=True),'compiler':subprocess.check_output(['xcrun','clang','--version'],text=True),'scope':'Modified six-bit expanded-reference numerical screen, no performance claim'}
        layout=json.loads((Path(MODEL)/'packed_experts/layout.json').read_text())
        assert layout['expertStride']==3342336 and layout['layerCount']==40 and layout['expertCount']==256
        expected=[('gate_proj.weight',0,1048576),('gate_proj.scales',1048576,32768),('gate_proj.biases',1081344,32768),('up_proj.weight',1114112,1048576),('up_proj.scales',2162688,32768),('up_proj.biases',2195456,32768),('down_proj.weight',2228224,1048576),('down_proj.scales',3276800,32768),('down_proj.biases',3309568,32768)]
        assert [(s['name'],s['offset'],s['size']) for s in layout['sections']]==expected
        (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        reference=Path('/Users/chad/Models/agentwing/evidence/AW-0037/20260906T063224.469387Z')
        for rel,h in json.loads((reference/'sha256.json').read_text()).items():assert digest(reference/rel)==h,rel
        manifest['reference_receipt_sha256']=digest(reference/'sha256.json')
        manifest['execution']='Expanded modified q8 through original fast8; no compressed-path throughput or residency claim'
        manifest['candidate']='q6-nearest-even-multiple4-clamp252-unchanged-bf16-metadata'
        (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        command=[str(binary),MODEL,str(run/'fixtures.json'),str(run/'Kernels.metal.txt'),str(run/'stages'),str(reference/'stages')];process=None;error=None;samples=[];baseline=host_sample()[1];start=time.monotonic()
        def interrupt(signum,frame):raise KeyboardInterrupt(str(signum))
        signal.signal(signal.SIGTERM,interrupt)
        try:
            with (run/'results.jsonl').open('w') as out,(run/'stderr.txt').open('w') as err:
                process=subprocess.Popen(command,stdout=out,stderr=err,start_new_session=True)
                while process.poll() is None:
                    sample=host_sample();samples.append([time.monotonic()-start,*sample]);check_sample(sample,baseline)
                    if time.monotonic()-start>300:raise RuntimeError('timeout')
                    time.sleep(.25)
        except (Exception,KeyboardInterrupt) as exc:error=str(exc) or type(exc).__name__
        finally:stop_group(process)
        result={'command':command,'exit':process.returncode if process else None,'error':error,'wall_seconds':time.monotonic()-start,'pressure_samples':samples,'swap_baseline_mib':baseline}
        (run/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        (run/'sha256.json').write_text(json.dumps({str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and p.name!='sha256.json'},indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='pressure_samples'}),flush=True);print((run/'stderr.txt').read_text())
        return 0 if result['exit']==0 and error is None else 1


if __name__=='__main__':raise SystemExit(main())
