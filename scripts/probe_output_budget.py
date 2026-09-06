#!/usr/bin/env python3
"""AW-0053 single larger-budget diagnostic; never executes tools."""
import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from run_local_agent import ROOT, preflight, host_sample, check_sample, stop_group, digest
from audit_sampling_capture import receipt_ok

CHECKOUT=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0053')
PLAN=ROOT/'evidence/AW-0053-budget-plan.json'

def main():
    plan=json.loads(PLAN.read_text())
    preflight()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=CHECKOUT,text=True).strip()
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=CHECKOUT,text=True).strip()==plan['runtime_revision']
    for path,expected in plan['hashes'].items():assert digest(path)==expected,path
    source=Path(plan['source_run']);assert receipt_ok(source)
    assert digest(source/'sha256-recursive.json')==plan['source_receipt_sha256']
    reference=[json.loads(line) for line in (source/'A1/sampling.jsonl').read_text().splitlines()]
    original=next(row for row in reference if row['event']=='end' and row['request']==1)
    prompt=json.loads(Path(plan['input']).read_text())
    run=Path('/Users/chad/Models/agentwing/evidence/AW-0053')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    run.mkdir(mode=0o700)
    shutil.copy2(PLAN,run/'plan.json');shutil.copy2(__file__,run/Path(__file__).name)
    shutil.copy2(plan['input'],run/'input.json')
    manifest={'plan_sha256':digest(PLAN),'runtime_revision':plan['runtime_revision'],
        'host':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['/usr/sbin/sysctl','-n','hw.model'],text=True).strip(),
        'thermal':subprocess.run(['pmset','-g','therm'],text=True,capture_output=True).stdout,
        'storage':subprocess.check_output(['df','-k',str(run)],text=True),'arms':[]}
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(run,flush=True)
    rows=[]
    for label,frequency in [('A1','0')]:
        directory=run/label;directory.mkdir();process=None;error=None;samples=[]
        baseline=host_sample()[1];started=time.monotonic()
        env={k:v for k,v in os.environ.items() if not k.startswith(('SWIFTLET_','AW53_'))}
        extra={**plan['environment'],'AW53_QPACK_DIR':plan['model'],'AW53_INPUT':str(run/'input.json'),
            'AW53_OUTPUT':str(directory/'report.json'),'AW53_FREQUENCY':frequency,
            'SWIFTLET_SAMPLING_TRACE':str(directory/'sampling.jsonl')}
        env.update(extra)
        command=[plan['testing_helper'],'--test-bundle-path',plan['test_binary'],
                 '--filter','OutputBudgetTests',plan['test_binary'],'--testing-library','swift-testing']
        (directory/'launch.json').write_text(json.dumps({'command':command,'environment':extra,'cwd':str(CHECKOUT)},indent=2)+'\n')
        try:
            with (directory/'test.log').open('w') as log, (directory/'pressure.jsonl').open('w') as pressure:
                process=subprocess.Popen(command,cwd=CHECKOUT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                (directory/'pid.json').write_text(json.dumps({'pid':process.pid})+'\n')
                while True:
                    sample=host_sample();reading=[time.monotonic()-started,*sample];samples.append(reading)
                    pressure.write(json.dumps(reading)+'\n');pressure.flush();check_sample(sample,baseline)
                    if process.poll() is not None:break
                    if time.monotonic()-started>plan['timeout_seconds_per_arm']:raise RuntimeError('timeout')
                    time.sleep(.5)
            if process.returncode!=0:raise RuntimeError('test-failed')
            trace=[json.loads(line) for line in (directory/'sampling.jsonl').read_text().splitlines()]
            assert trace[0]['event']=='begin' and trace[-1]['event']=='end'
            begin,end=trace[0],trace[-1]
            assert begin['actual_prompt_ids']==prompt['actual_prompt_ids']==begin['rendered_prompt_ids']
            assert begin['new_prompt_tokens']==len(prompt['actual_prompt_ids']) and begin['reused_prompt_tokens']==0
            for key in ['temperature','presence_penalty','no_repeat_ngram','min_new','top_k','top_p','eos_ids','suppressed_ids','stop_sequences','stop_after_sequences']:
                assert begin[key]==prompt[key],key
            assert begin['frequency_penalty']==float(frequency) and begin['admitted_max_new']==1024
            report=json.loads((directory/'report.json').read_text());assert report['text']==end['text']
            equal=end['generated_ids'][:512]==original['generated_ids']
            old_decisions=[d for d in reference if d['event']=='decision']
            new_decisions=[d for d in trace if d['event']=='decision']
            keys=['selected','seen_before','selected_raw','selected_adjusted','raw','adjusted','ban_eos','is_eos']
            equal=equal and len(new_decisions)>=512 and len(old_decisions)==512 and all(
                all(a[k]==b[k] for k in keys) for a,b in zip(new_decisions[:512],old_decisions))
            if not equal:raise RuntimeError('extended-budget-prefix-does-not-match-zero-penalty-reference')
        except (Exception,KeyboardInterrupt) as exc:error=str(exc) or type(exc).__name__
        finally:stop_group(process)
        row={'arm':label,'frequency_penalty':float(frequency),'exit':process.returncode if process else None,
             'error':error,'wall_seconds':time.monotonic()-started,'swap_baseline_mib':baseline,
             'peak_pressure':max(s[1] for s in samples) if samples else None,
             'peak_swap_growth_mib':max(s[2]-baseline for s in samples) if samples else None}
        (directory/'result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(json.dumps(row),flush=True)
        if error:break
    summary={'sequence_complete':len(rows)==1 and all(r['error'] is None for r in rows),'arms':rows,
        'scope':'Model-only budget diagnostic; matching prefix is not protocol/content success; independent output review required; no endpoint or promotion claim.'}
    (run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (run/'sha256-recursive.json').write_text(json.dumps({str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and p.name!='sha256-recursive.json'},indent=2)+'\n')
    return 0 if summary['sequence_complete'] else 1

if __name__=='__main__':
    with (ROOT/'var/local-agent.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        raise SystemExit(main())
