#!/usr/bin/env python3
"""AW-0046 isolated functional C/A/C oracle; deliberately not a speed test."""
import datetime
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time
from run_local_agent import ROOT, preflight, host_sample, check_sample, stop_group, digest

CHECKOUT = Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0046')
MODEL = '/Users/chad/Models/agentwing/checkpoints/qwen3.6-35b-a3b-8bit.qpack'

def main():
    preflight()
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=CHECKOUT, text=True).strip()
    binary = CHECKOUT / '.build/release/SwiftletPackageTests.xctest/Contents/MacOS/SwiftletPackageTests'
    assert binary.is_file()
    source = CHECKOUT / 'Tests/SwiftletCoreTests/RealUnionBoundaryTests.swift'
    assert digest(source) == digest(ROOT / 'probes/runtime_overlap/RealUnionBoundaryTests.swift')
    run = Path('/Users/chad/Models/agentwing/evidence/AW-0046') / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    run.mkdir(mode=0o700)
    sources = [Path(__file__), ROOT/'probes/runtime_overlap/RealUnionBoundaryTests.swift',
               ROOT/'scripts/run_local_agent.py', CHECKOUT/'Sources/SwiftletCore/QwenMetalModel.swift',
               CHECKOUT/'Sources/SwiftletCore/ExpertCache.swift']
    for p in sources:
        (run/p.name).write_bytes(p.read_bytes())
    plan = [('C1', 'reference'), ('A1', 'candidate'), ('C2', 'reference')]
    manifest = {'runtime_revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=CHECKOUT,text=True).strip(),
                'order': plan, 'model': MODEL, 'reference_cache_gib': 1.0, 'candidate_cache_gib': 0.5,
                'chunk_tokens': 256, 'prefix_tokens': 256, 'seed_hex': '41573436424F554E',
                'greedy_steps': 8, 'timeout_seconds_per_arm': 900,
                'scope': 'Synthetic full-model cache-boundary functional oracle; not capability or throughput evidence',
                'hashes': {str(p):digest(p) for p in [*sources,binary,CHECKOUT/'.build/release/Swiftlet_SwiftletCore.bundle/Kernels.metal.txt']}}
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(str(run), flush=True)
    rows=[]
    for label, arm in plan:
        directory=run/label;directory.mkdir();process=None;error=None;samples=[]
        baseline=host_sample()[1];started=time.monotonic()
        env={k:v for k,v in os.environ.items() if not k.startswith(('SWIFTLET_','AW46_'))}
        env.update(AW46_QPACK_DIR=MODEL,AW46_BOUNDARY_ARM=arm,AW46_BOUNDARY_OUTPUT=str(directory))
        command=['swift','test','-c','release','--skip-build','--disable-automatic-resolution','--filter','RealUnionBoundaryTests']
        try:
            with (directory/'test.log').open('w') as log:
                process=subprocess.Popen(command,cwd=CHECKOUT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                while True:
                    sample=host_sample();samples.append([time.monotonic()-started,*sample]);check_sample(sample,baseline)
                    if process.poll() is not None:break
                    if time.monotonic()-started>900:raise RuntimeError('timeout')
                    time.sleep(.25)
            if process.returncode!=0:raise RuntimeError('test-failed')
        except (Exception,KeyboardInterrupt) as exc:error=str(exc) or type(exc).__name__
        finally:stop_group(process)
        row={'arm':label,'mode':arm,'command':command,'exit':process.returncode if process else None,
             'error':error,'wall_seconds':time.monotonic()-started,'swap_baseline_mib':baseline,
             'pressure_samples':samples}
        (directory/'result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
        print(json.dumps({k:v for k,v in row.items() if k not in ['pressure_samples','command']}),flush=True)
        if error:break
    complete=len(rows)==3 and all(r['error'] is None for r in rows)
    checks={}
    if complete:
        reports=[json.loads((run/label/'model-report.json').read_text()) for label,_ in plan]
        for key in ['tokens','generated','routes','unions']:
            checks[key]=reports[0][key]==reports[1][key]==reports[2][key]
        checks['real_oversized_unions']=all(r['maximum_union']>160 for r in reports)
        checks['only_candidate_streamed']=reports[0]['streamed_windows']==reports[2]['streamed_windows']==0 and reports[1]['streamed_windows']>0
        checks['physical_budgets']=all(r['allocated_bytes']<=r['cache_budget_bytes'] for r in reports)
        checks['candidate_budget_unchanged']=reports[1]['cache_budget_bytes']==536870912
        checks['all_nine_logits_exact']=all(len({digest(run/label/f'logits-{i}.bin') for label,_ in plan})==1 for i in range(9))
    summary={'complete':complete,'passed':complete and all(checks.values()),'checks':checks,'arms':rows,
             'scope':manifest['scope']}
    (run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (run/'sha256.json').write_text(json.dumps({str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and p.name!='sha256.json'},indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='arms'}),flush=True)
    return 0 if summary['passed'] else 1

if __name__=='__main__':
    with (ROOT/'var/local-agent.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        raise SystemExit(main())
