#!/usr/bin/env python3
"""AW-0044 development agent runs with frozen P1 or an explicitly pinned candidate."""
from collections import Counter
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
from run_local_agent import ROOT, digest, execute, pi_command, preflight
from verify_p2_task import SUITE, verify
from audit_stage_a import METRIC, has_terminal_boundary


def protocol_audit(directory):
    events=[json.loads(s) for s in (directory/'pi.jsonl').read_text().splitlines() if s.strip()]
    log=(directory/'server.log').read_text();lines=log.splitlines()
    metrics=[m for s in lines if (m:=METRIC.fullmatch(s))]
    pending=set();seen=set();starts=[];ends=[];paired=True;commands=[]
    for e in events:
        if e.get('type')=='tool_execution_start':
            key=e.get('toolCallId');paired &= bool(key) and key not in seen
            seen.add(key);pending.add(key);starts.append(e);commands.append(e.get('args',{}).get('command'))
        elif e.get('type')=='tool_execution_end':
            key=e.get('toolCallId');paired &= key in pending;pending.discard(key);ends.append(e)
    checks={'events_nonempty':bool(events),'paired_unique_tool_events':paired and not pending and len(starts)==len(ends),
            'bash_schema_valid':all(e.get('toolName')=='bash' and isinstance(e.get('args',{}).get('command'),str) and bool(e['args']['command'].strip()) for e in starts),
            'no_model_error':not any(e.get('type')=='message_end' and e.get('message',{}).get('stopReason')=='error' for e in events),
            'no_server_tool_rejection':'rejected tool output:' not in log,
            'fresh_model_state':bool(metrics) and int(metrics[0][3])==0,
            'unique_requests':len({m[1] for m in metrics})==len(metrics),
            'terminal_metric':has_terminal_boundary(lines),
            'no_explicit_authority_access':not any('benchmarks/p2-v1/authorities' in (c or '') for c in commands)}
    return {'passed':all(checks.values()),'checks':checks,'tool_calls':len(starts),
            'failed_tool_calls':sum(bool(e.get('isError')) for e in ends),
            'repeated_command_occurrences':sum(n-1 for n in Counter(c for c in commands if isinstance(c,str)).values()),
            'productivity_classification':'not inferred from command success; full transcript retained for separate review',
            'request_count':len(metrics),'new_prompt_tokens':sum(int(m[2]) for m in metrics),
            'generated_tokens':sum(int(m[5]) for m in metrics),'reported_ttft_seconds':sum(float(m[6]) for m in metrics),
            'declared_normalizations':log.count('normalized declared schema-property tags'),
            'declared_salvages':log.count('salvaged complete tool-call prefix')}


def select_tasks(manifest, selection):
    development=[t for t in manifest['tasks'] if t['split']=='development']
    selected=development if selection=='all' else [t for t in development if t['id']==selection]
    if not selected:raise ValueError('This runner accepts only frozen development tasks')
    return selected


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);parser.add_argument('--candidate-plan',type=Path);parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    manifest=json.loads((SUITE/'manifest.json').read_text());selected=select_tasks(manifest,args.task)
    candidate=json.loads(args.candidate_plan.read_text()) if args.candidate_plan else None
    if candidate:
        assert digest(candidate['server_binary'])==candidate['server_binary_sha256']
        for file,sha in candidate['runtime_files'].items():assert digest(file)==sha,file
        checkout=Path(candidate['checkout'])
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()==candidate['source_revision']
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True).strip()
        assert set(candidate['environment'])<= {'SWIFTLET_EXPERT_OVERLAP','SWIFTLET_CHUNK_OVERLAP','SWIFTLET_CHUNK_FULL_OVERLAP'}
        assert all(v=='1' for v in candidate['environment'].values())
    profile=candidate['id'] if candidate else 'P1'
    (ROOT/'var').mkdir(exist_ok=True)
    with (ROOT/'var/local-agent.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        subprocess.run(['/usr/bin/python3',str(ROOT/'scripts/freeze_p2_suite.py')],check=True)
        preflight()
        if args.check_only:
            print(json.dumps({'selected':[t['id'] for t in selected],'profile':profile,'timeout_seconds':manifest['default_timeout_seconds']}));return 0
        started=time.monotonic();root=Path('/Users/chad/Models/agentwing/evidence/AW-0044');root.mkdir(exist_ok=True)
        run=root/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(mode=0o700)
        deps=json.loads((ROOT/'spec/dependencies.json').read_text())
        server=[str(Path(deps['swiftlet']['local_path'])/'.build/release/swiftlet-server'),'--model',deps['qwen3_6_35b_a3b_8bit_qpack']['local_path'],'--port','8080','--cache-gb','0.5','--debug-tool-output','--accept-schema-tags','--salvage-tool-prefix','--allow-repeated-ngrams','--stop-after-tool-call']
        real_binary=server[0]
        if candidate:
            real_binary=candidate['server_binary']
            server=['/usr/bin/env',*[f'{k}={v}' for k,v in sorted(candidate['environment'].items())],real_binary,*server[1:]]
            (run/'candidate-plan.json').write_bytes(args.candidate_plan.read_bytes())
        source_files=['scripts/run_development_candidate.py','scripts/run_p2_development.py','scripts/run_local_agent.py','scripts/verify_p2_task.py','scripts/audit_stage_a.py','scripts/run_task_boundary.py']
        record={'profile':profile,'scope':'Development diagnostic only; not held-out or paired promotion evidence','selection':[t['id'] for t in selected],
                'task_timeout_seconds':manifest['default_timeout_seconds'],'timeout_scope':'Pi execution; startup separately capped at 60s; all overhead charged',
                'corpus_receipt_sha256':digest(ROOT/'evidence/AW-0034-corpus-freeze-v1.json'),'server_command':server,'server_binary':real_binary,'server_binary_sha256':digest(real_binary),'candidate_plan_sha256':digest(args.candidate_plan) if candidate else None,
                'source_hashes':{p:digest(ROOT/p) for p in source_files},'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),
                'thermal_before':subprocess.check_output(['pmset','-g','therm'],text=True),'free_bytes_before':shutil.disk_usage(run).free,
                'inherited_runtime_environment':{k:v for k,v in os.environ.items() if k.startswith(('SWIFTLET_','AGENTWING_'))}}
        if record['inherited_runtime_environment']:raise RuntimeError('Unexpected runtime environment overrides')
        (run/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
        for p in source_files:(run/Path(p).name).write_bytes((ROOT/p).read_bytes())
        def interrupted(signum,frame):raise KeyboardInterrupt(f'signal-{signum}')
        signal.signal(signal.SIGTERM,interrupted)
        print(f'run_dir={run}',flush=True);rows=[];error=None
        try:
            for task in selected:
                preflight();task_start=time.monotonic();directory=run/task['id'];directory.mkdir()
                shutil.copytree(SUITE/'tasks'/task['id']/'input',directory/'workspace')
                (directory/'task.txt').write_text(task['prompt'])
                shutil.copyfile(ROOT/'config/pi-models-validated.json',directory/'pi-models.json')
                shutil.copyfile(ROOT/'config/validated-local-agent-prompt.txt',directory/'system-prompt.txt')
                report=execute(directory,server,pi_command(directory/'workspace',directory/'pi-models.json',task['prompt']),timeout=manifest['default_timeout_seconds'])
                protocol=protocol_audit(directory)
                grading=verify(task['id'],directory/'workspace')
                good=report['status']=='client-completed' and report['error'] is None and protocol['passed']
                row={'task_id':task['id'],'category':task['category'],'utility':grading['utility'] if good else 0,
                     'execution':report,'protocol':protocol,'grading':grading,'full_wall_seconds':time.monotonic()-task_start}
                (directory/'scored-result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
                print(json.dumps({k:row[k] for k in ['task_id','utility','full_wall_seconds']}),flush=True)
                if report['error'] is not None:raise RuntimeError(report['error'])
        except (Exception,KeyboardInterrupt) as exc:error=str(exc) or type(exc).__name__
        finally:
            wall=time.monotonic()-started;utility=sum(r['utility'] for r in rows)
            summary={'complete_selection':len(rows)==len(selected) and error is None,'error':error,'wall_seconds':wall,'utility':utility,'verified_utility_per_hour':utility*3600/wall,'tasks':rows,'scope':record['scope']}
            (run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
            (run/'sha256-recursive.json').write_text(json.dumps({str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and not p.is_symlink() and p.name!='sha256-recursive.json'},indent=2)+'\n')
        print(json.dumps({k:v for k,v in summary.items() if k!='tasks'}),flush=True)
        return 0 if summary['complete_selection'] else 1


if __name__=='__main__':raise SystemExit(main())
