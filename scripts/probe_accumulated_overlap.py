#!/usr/bin/env python3
"""AW-0042 supervised interleaved runtime overlap diagnostic."""
from collections import Counter
import datetime
import fcntl
import json
import os
from pathlib import Path
import signal
import struct
import subprocess
import time
from run_local_agent import preflight, host_sample, check_sample, stop_group, digest
from probe_expert_residency import MODEL, PROMPT

ROOT=Path(__file__).resolve().parents[1]
CHECKOUT=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0042')
CASES=[
 ('rust-queue','Design a bounded multi-producer single-consumer queue in Rust. Explain ownership, synchronization, backpressure, cancellation, and shutdown races. Include a compact implementation sketch and discuss how you would test producer failure while the consumer drains pending items. Give a detailed technical answer with explicit invariants.'),
 ('unicode-records','Design a robust data-cleaning pipeline for multilingual contact records with Unicode names, inconsistent dates, duplicate identifiers, and missing fields. Explain normalization, stable deduplication, provenance, reversible migrations, and validation. Include concrete Python examples covering accented Latin, Arabic, and Japanese names, and describe useful property-based tests.')
]


def main():
    preflight();binary=CHECKOUT/'.build/release/swiftlet'
    assert binary.is_file(),'Build isolated capture runtime before running'
    root=Path('/Users/chad/Models/agentwing/evidence/AW-0042');root.mkdir(exist_ok=True)
    run=root/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(mode=0o700)
    sampler=Path('/Users/chad/Models/agentwing/evidence/AW-0031/process_io_trace')
    assert sampler.is_file()
    (run/'process_io_trace.m').write_bytes((ROOT/'probes/process_io_trace.m').read_bytes())
    plan=[(name,label,prompt,enabled) for name,prompt in CASES for label,enabled in [('C1',False),('A1',True),('C2',False)]]
    sources=['Sources/SwiftletCore/ExpertActivationTrace.swift','Sources/SwiftletCore/Qpack.swift','Sources/SwiftletCore/ExpertCache.swift','Sources/SwiftletCore/QwenMetalModel.swift']
    manifest={'cases':CASES,'order':[name+'-'+label for name,label,_,_ in plan],'binary_sha256':digest(binary),'sampler_sha256':digest(sampler),'script_sha256':digest(__file__),
              'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=CHECKOUT,text=True).strip(),'source_sha256':{p:digest(CHECKOUT/p) for p in sources},
              'max_new':64,'cache_gb':.5,'model':MODEL,'os':subprocess.check_output(['sw_vers'],text=True),
              'scope':'Longer accumulated-activation diagnostic; common observer, no held-out or endpoint claim'}
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (run/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    for p in sources:(run/Path(p).name).write_bytes((CHECKOUT/p).read_bytes())
    print(run,flush=True);results=[]
    def interrupt(signum,frame):raise KeyboardInterrupt(str(signum))
    signal.signal(signal.SIGTERM,interrupt)
    for name,label,prompt,enabled in plan:
        preflight();directory=run/(name+'-'+label);directory.mkdir();process=io_process=None;error=None;samples=[];baseline=host_sample()[1];start=time.monotonic()
        env={k:v for k,v in os.environ.items() if not k.startswith('SWIFTLET_')};env['PYTHONDONTWRITEBYTECODE']='1'
        env['SWIFTLET_EXPERT_TRACE']=str(directory/'routes.jsonl')
        env['SWIFTLET_ACTIVATION_TRACE']=str(directory/'activations.jsonl')
        if enabled:
            env['SWIFTLET_EXPERT_OVERLAP']='1'
            env['SWIFTLET_CHUNK_OVERLAP']='1'
        command=[str(binary),'generate',MODEL,'--gpu','--cache-gb','0.5','--prompt',prompt,'--max-new','64']
        try:
            with (directory/'stdout.txt').open('w') as out,(directory/'stderr.txt').open('w') as err,(directory/'io.jsonl').open('w') as io:
                process=subprocess.Popen(command,stdout=out,stderr=err,start_new_session=True,env=env)
                io_process=subprocess.Popen([str(sampler),str(process.pid)],stdout=io,stderr=subprocess.DEVNULL,start_new_session=True)
                while process.poll() is None:
                    sample=host_sample();samples.append([time.monotonic()-start,*sample]);check_sample(sample,baseline)
                    if time.monotonic()-start>300:raise RuntimeError('timeout')
                    time.sleep(.25)
            if process.returncode!=0:raise RuntimeError('generation failed')
        except (Exception,KeyboardInterrupt) as exc:error=str(exc) or type(exc).__name__
        finally:stop_group(process);stop_group(io_process)
        row={'case':name,'arm':label,'exit':process.returncode if process else None,'error':error,'wall_seconds':time.monotonic()-start,'swap_baseline_mib':baseline,'pressure_samples':samples}
        (directory/'result.json').write_text(json.dumps(row,indent=2)+'\n');results.append(row)
        print(json.dumps({k:v for k,v in row.items() if k!='pressure_samples'}),flush=True)
        if error is not None:break
    complete=len(results)==len(plan) and all(r['error'] is None for r in results)
    output_equivalence={name:len({digest(run/(name+'-'+label)/'stdout.txt') for label in ['C1','A1','C2']})==1 for name,_ in CASES} if complete else {}
    def routes(name,label):
        return [(r['layer'],r['experts']) for r in map(json.loads,(run/(name+'-'+label)/'routes.jsonl').read_text().splitlines()) if r['event']=='route']
    route_equivalence={name:routes(name,'C1')==routes(name,'A1')==routes(name,'C2') for name,_ in CASES} if complete else {}
    summary={'route_equivalence':route_equivalence,'complete':complete,'all_outputs_match':complete and all(output_equivalence.values()) and all(route_equivalence.values()),'output_equivalence':output_equivalence,'arms':results}
    (run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (run/'sha256.json').write_text(json.dumps({str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and p.name!='sha256.json'},indent=2)+'\n')
    return 0 if summary['all_outputs_match'] else 1


if __name__=='__main__':
    with (ROOT/'var/local-agent.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        raise SystemExit(main())
