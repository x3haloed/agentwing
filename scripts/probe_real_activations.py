#!/usr/bin/env python3
"""AW-0036 bounded source-activation capture; requires isolated built runtime."""
from collections import Counter
import datetime
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
CHECKOUT=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0036')
CASES=[('coding',PROMPT),('arithmetic','Explain why the sum of two even integers is even. Give a short algebraic argument.'),('structured','Return a JSON object describing a fictional library book with title, author, year, and a list of three tags.')]


def audit_capture(path):
    rows=[json.loads(s) for s in path.read_text().splitlines()]
    assert 0<len(rows)<=24 and [r['sequence'] for r in rows]==list(range(len(rows)))
    trace=[json.loads(s) for s in (path.parent/'routes.jsonl').read_text().splitlines()]
    assert len(trace)<10000 and [r['sequence'] for r in trace]==list(range(len(trace)))
    by_layer={}
    for r in trace:
        if r['event']=='route':by_layer.setdefault(r['layer'],[]).append(r['experts'])
    counts=Counter((r['layer'],r['schedule']) for r in rows)
    assert set(counts)=={(layer,phase) for layer in [0,20,39] for phase in ['single-token','chunked-prefill']}
    assert all(1<=n<=4 for n in counts.values())
    for r in rows:
        assert by_layer[r['layer']][r['position']]==r['experts'], 'capture/route position mismatch'
        assert len(r['input_f32_bits'])==2048 and len(r['experts'])==len(r['weights_f32_bits'])==8
        assert len(set(r['experts']))==8 and all(0<=e<256 for e in r['experts'])
        for field in ['input_f32_bits','weights_f32_bits']:
            assert all(type(b) is int and 0<=b<2**32 and (b & 0x7f800000)!=0x7f800000 for b in r[field])
        weights=[struct.unpack('<f',struct.pack('<I',b))[0] for b in r['weights_f32_bits']]
        assert all(w>=0 for w in weights) and abs(sum(weights)-1)<1e-5
    return {'records':len(rows),'schedule_layer_counts':{f'{layer}:{phase}':n for (layer,phase),n in counts.items()},'exact_f32_bit_pattern_validation':True}


def main():
    preflight();binary=CHECKOUT/'.build/release/swiftlet'
    assert binary.is_file(),'Build isolated capture runtime before running'
    root=Path('/Users/chad/Models/agentwing/evidence/AW-0036');root.mkdir(exist_ok=True)
    run=root/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(mode=0o700)
    plan=[(name,label,prompt,enabled) for name,prompt in CASES for label,enabled in [('C1',False),('A1',True),('C2',False)]]
    sources=['Sources/SwiftletCore/ExpertActivationTrace.swift','Sources/SwiftletCore/QwenMetalModel.swift']
    manifest={'cases':CASES,'order':[name+'-'+label for name,label,_,_ in plan],'binary_sha256':digest(binary),'script_sha256':digest(__file__),
              'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=CHECKOUT,text=True).strip(),'source_sha256':{p:digest(CHECKOUT/p) for p in sources},
              'max_new':12,'cache_gb':.5,'model':MODEL,'os':subprocess.check_output(['sw_vers'],text=True),
              'scope':'Source-activation diagnostic, no quantized candidate or held-out agent task'}
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (run/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    for p in sources:(run/Path(p).name).write_bytes((CHECKOUT/p).read_bytes())
    print(run,flush=True);results=[]
    def interrupt(signum,frame):raise KeyboardInterrupt(str(signum))
    signal.signal(signal.SIGTERM,interrupt)
    for name,label,prompt,enabled in plan:
        preflight();directory=run/(name+'-'+label);directory.mkdir();process=None;error=None;samples=[];baseline=host_sample()[1];start=time.monotonic()
        env={k:v for k,v in os.environ.items() if not k.startswith('SWIFTLET_')};env['PYTHONDONTWRITEBYTECODE']='1'
        env['SWIFTLET_EXPERT_TRACE']=str(directory/'routes.jsonl')
        if enabled:env['SWIFTLET_ACTIVATION_TRACE']=str(directory/'activations.jsonl')
        command=[str(binary),'generate',MODEL,'--gpu','--cache-gb','0.5','--prompt',prompt,'--max-new','12']
        try:
            with (directory/'stdout.txt').open('w') as out,(directory/'stderr.txt').open('w') as err:
                process=subprocess.Popen(command,stdout=out,stderr=err,start_new_session=True,env=env)
                while process.poll() is None:
                    sample=host_sample();samples.append([time.monotonic()-start,*sample]);check_sample(sample,baseline)
                    if time.monotonic()-start>180:raise RuntimeError('timeout')
                    time.sleep(.25)
            if process.returncode!=0:raise RuntimeError('generation failed')
            if enabled:audit_capture(directory/'activations.jsonl')
        except (Exception,KeyboardInterrupt) as exc:error=str(exc) or type(exc).__name__
        finally:stop_group(process)
        row={'case':name,'arm':label,'exit':process.returncode if process else None,'error':error,'wall_seconds':time.monotonic()-start,'swap_baseline_mib':baseline,'pressure_samples':samples}
        if error is None and enabled:row['capture_audit']=audit_capture(directory/'activations.jsonl')
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


if __name__=='__main__':raise SystemExit(main())
