#!/usr/bin/env python3
"""AW-0159 isolated rollback allocation admission; no generation requests."""
import fcntl,json,re,subprocess,time,urllib.request
from pathlib import Path
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample,stop_group,ready
from bonsai_turbo_server import command,verify,SPEC

def main():
    r=Path('/Users/chad/Models/agentwing/evidence/AW-0159')
    r.mkdir(exist_ok=True)
    assert not (r/'plan.json').exists(), 'Preserve prior run; do not overwrite'
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        preflight();verify()
        receipt_path=ROOT/'evidence/AW-0158-ngram-rollback-build.json'
        receipt=json.loads(receipt_path.read_text());binary=Path(receipt['build'])/'bin/llama-server'
        for name,expected in receipt['artifacts_sha256'].items():
            assert digest(binary.parent/name)==expected, name
        for name,expected in receipt['patches'].items():
            assert digest(ROOT/name)==expected, name
        cmd=command();cmd[0]=str(binary)
        cmd+=['--spec-type','ngram-simple','--spec-ngram-simple-size-n','2',
              '--spec-ngram-simple-size-m','3','--verbose']
        plan={'experiment':'AW-0159','hypothesis':'Isolated server allocates three recurrent rollback slots with full vision and compressed KV under existing host gates.',
              'primary_metric':'Actual allocation/health/clean exit and pressure/swap gates; no performance or generation claim.',
              'command':cmd,'harness_sha256':digest(Path(__file__)),
              'parent_build_receipt_sha256':digest(receipt_path),'parent_runtime_spec_sha256':digest(SPEC),
              'runtime_build':receipt,'sampling_context_vision':json.loads(SPEC.read_text()),
              'os':subprocess.check_output(['sw_vers'],text=True),
              'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),
              'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),
              'storage':'internal SSD','cache':'Fresh server; uncontrolled OS page cache; no speed comparison',
              'startup_timeout_s':60,'requests':'GET health/props only; no generation/tools',
              'acceptance':'n_rs_seq=3, recurrent598.50MiB within1MiB, q8K/Turbo4V408MiB, enabled ngram-simple, HTTP200, pressure<4, swap growth<=1024MiB, clean cleanup.'}
        (r/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
        baseline=host_sample()[1];samples=[];server=None;error=None;statuses={};start=time.monotonic()
        with (r/'server.log').open('w') as log,(r/'pressure.jsonl').open('w') as pressure:
            try:
                check_sample(host_sample(),baseline)
                server=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                deadline=time.monotonic()+60
                while not ready():
                    sample=host_sample();samples.append(sample);check_sample(sample,baseline)
                    pressure.write(json.dumps({'time':time.time(),'pressure':sample[0],'swap_mib':sample[1]})+'\n');pressure.flush()
                    if server.poll() is not None or time.monotonic()>deadline:raise RuntimeError('startup failed')
                    time.sleep(.5)
                opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
                for path in ['health','props']:
                    with opener.open('http://127.0.0.1:8080/'+path,timeout=3) as response:
                        statuses[path]=response.status;(r/(path+'.json')).write_bytes(response.read())
                sample=host_sample();samples.append(sample);check_sample(sample,baseline)
            except Exception as exc:error=str(exc)
            finally:stop_group(server)
        text=(r/'server.log').read_text()
        allocation=[float(x) for x in re.findall(r'RS buffer size =\s*([\d.]+) MiB',text)]
        checks={'slots3':bool(re.search(r'n_rs_seq\s*=\s*3',text)),
                'rs_allocation':bool(allocation) and all(abs(x-598.50)<1 for x in allocation),
                'ngram_enabled':'speculative decoding enabled: ngram-simple' in text,
                'bounded_rollback':'context supports bounded partial sequence removal' in text,
                'http200':statuses=={'health':200,'props':200},
                'clean_exit':server is not None and server.returncode==0}
        result={'experiment':'AW-0159','error':error,'checks':checks,'passed':error is None and all(checks.values()),
                'recurrent_allocations_mib':allocation,'server_exit':server.returncode if server else None,
                'baseline_swap_mib':baseline,'pressure_peak':max((s[0] for s in samples),default=None),
                'swap_growth_peak_mib':max((max(0,s[1]-baseline) for s in samples),default=None),
                'wall_seconds_diagnostic':time.monotonic()-start,'generation_requests':0,'tools_executed':0,
                'raw_sha256':{p.name:digest(p) for p in r.iterdir() if p.is_file()},
                'scope':'Allocation/startup only; rollback fidelity, actual cost and endpoint utility unproven.'}
        (r/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result|{'raw_sha256':'saved'}),flush=True)
        if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
