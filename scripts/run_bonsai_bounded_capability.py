#!/usr/bin/env python3
"""Frozen full original supported-thinking diagnostic with bounded state caches."""
import argparse
from collections import Counter
import datetime
import fcntl
import json
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
from bonsai_server import ROOT, command as base_command, verify as verify_artifacts
from run_local_agent import execute, preflight, digest
from stable_workspace import staged_workspace
from verify_original_copy import SUITE, verify as grade

PLAN = ROOT/'evidence/AW-0070-original-plan.json'


def command():
    cmd=base_command()
    return cmd+['--ctx-checkpoints','2','--cache-ram','0','--no-context-shift','--log-verbosity','5','--presence-penalty','0','--frequency-penalty','0']
LIVE = Path('/Users/chad/Models/agentwing/active')


def protocol(directory):
    events=[json.loads(l) for l in (directory/'pi.jsonl').read_text().splitlines() if l.strip()]
    log=(directory/'server.log').read_text()
    starts=[e for e in events if e.get('type')=='tool_execution_start']
    ends=[e for e in events if e.get('type')=='tool_execution_end']
    pending=set();seen=set();paired=True
    for e in events:
        if e.get('type')=='tool_execution_start':
            key=e.get('toolCallId');paired &= bool(key) and key not in seen;seen.add(key);pending.add(key)
        elif e.get('type')=='tool_execution_end':
            key=e.get('toolCallId');paired &= key in pending;pending.discard(key)
    launches=re.findall(r'launch_slot_.*?task\s+(\d+)\s+\| processing task',log)
    releases=re.findall(r'release:.*?task\s+(\d+)\s+\| stop processing:',log)
    checks={'events_nonempty':bool(events),'paired_unique_calls':paired and not pending and len(starts)==len(ends),
            'bash_schema_valid':all(e.get('toolName')=='bash' and isinstance(e.get('args',{}).get('command'),str) and bool(e['args']['command'].strip()) for e in starts),
            'no_model_errors':not any(e.get('type')=='message_end' and e.get('message',{}).get('stopReason')=='error' for e in events),
            'fresh_model_load':"model loaded" in log and "n_slots = 1" in log,
            'serialized_unique_requests':bool(launches) and len(set(launches))==len(launches),
            'all_requests_terminal':Counter(launches)==Counter(releases),
            'server_cleanup':'cleaning up before exit' in log,
            'no_explicit_authority_access':not any('benchmarks/p2-v1/authorities' in e.get('args',{}).get('command','') for e in starts)}
    return {'passed':all(checks.values()),'checks':checks,'tool_accounting':{'attempted':len(starts),'valid':len(starts) if checks['bash_schema_valid'] else None,
             'productive':None,'redundant':None,'malformed':0 if checks['no_model_errors'] and checks['bash_schema_valid'] else None,
             'denied':None,'failed':sum(bool(e.get('isError')) for e in ends)},
            'commands':[e['args']['command'] for e in starts], 'request_count':len(launches),
            'classification':'Productivity, redundancy and denial need separate transcript review; raw events retained.'}


def freeze():
    if PLAN.exists():raise RuntimeError('Plan exists; never overwrite frozen experiment')
    suite=json.loads((SUITE/'manifest.json').read_text())
    sources=['scripts/run_bonsai_bounded_capability.py','scripts/bonsai_server.py','scripts/run_local_agent.py','scripts/stable_workspace.py',
             'scripts/run_task_boundary.py','scripts/verify_original_copy.py','scripts/verify_stage_a.py','config/pi-bonsai-thinking-models.json',
             'config/task-boundary.sb','config/validated-local-agent-prompt.txt','spec/bonsai-local.json','spec/bonsai-bounded-cache.json','spec/validated-local-agent.json',
             'spec/p2-acceptance.json','evidence/AW-0034-corpus-freeze-v1.json']
    pins={p:digest(ROOT/p) for p in sources}
    pins.update({str(p.relative_to(ROOT)):digest(p) for p in SUITE.rglob('*') if p.is_file()})
    plan={'experiment':'AW-0070','scope':'Complete original capability diagnostic; publisher thinking sampler, full 8K context and medium reasoning, prompt archive disabled, recurrent checkpoint count bounded to two. No comparative speed or promotion claim',
          'selection':[t['id'] for t in suite['tasks']],'successes_required':8,'stop_on_first_failure':True,
          'task_timeout_seconds':suite['default_timeout_seconds'],'startup_timeout_seconds':60,'pins':pins,
          'candidate':json.loads((ROOT/'spec/bonsai-bounded-cache.json').read_text()),'system_prompt':'config/validated-local-agent-prompt.txt',
          'thinking':'medium','tools':['bash'],'workspace_path':str(LIVE/'workspace'),'permissions':'workspace-state-write-local-outbound-v1',
          'network':'acquisition already complete; task network restricted to loopback; no benchmark authority passed to model'}
    PLAN.write_text(json.dumps(plan,indent=2)+'\n')


def client(workspace,models,task):
    node=json.loads((ROOT/'spec/validated-local-agent.json').read_text())['environment']['AGENTWING_NODE_BIN']
    return ['/usr/bin/python3',str(ROOT/'scripts/run_task_boundary.py'),'--workspace',str(workspace),'--models-file',str(models),'--',node,
            str(ROOT/'node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js'),'--provider','agentwing-bonsai','--model','bonsai2-27b',
            '--thinking','medium','--mode','json','--print','--no-session','--approve','--offline','--tools','bash',
            '--system-prompt',(ROOT/'config/validated-local-agent-prompt.txt').read_text().rstrip('\n'),task]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');p.add_argument('--check-only',action='store_true');args=p.parse_args()
    if args.freeze:freeze();print(f'Frozen {PLAN}');return
    plan=json.loads(PLAN.read_text())
    for path,h in plan['pins'].items():
        if digest(ROOT/path)!=h:raise RuntimeError(f'Frozen input changed: {path}')
    subprocess.run(['/usr/bin/python3',str(ROOT/'scripts/freeze_p2_suite.py')],check=True)
    preflight()
    if args.check_only:print(json.dumps({'plan_sha256':digest(PLAN),'selection':plan['selection'],'status':'pass'}));return
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        started=time.monotonic()
        root=Path('/Users/chad/Models/agentwing/evidence/AW-0070');root.mkdir(exist_ok=True)
        run=root/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(mode=0o700)
        print(f'run_dir={run}',flush=True)
        record={'plan_sha256':digest(PLAN),'scope':plan['scope'],'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                'os':subprocess.check_output(['sw_vers'],text=True),'host':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),
                'storage':'internal SSD','free_bytes':shutil.disk_usage(run).free,'cache':'fresh model process per task; existing OS page cache uncontrolled',
                'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'server_command':command(),'configuration':plan['candidate']}
        (run/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');(run/'plan.json').write_bytes(PLAN.read_bytes())
        def interrupt(signum,frame):raise KeyboardInterrupt(f'signal-{signum}')
        signal.signal(signal.SIGTERM,interrupt)
        tasks=[t for t in json.loads((SUITE/'manifest.json').read_text())['tasks'] if t['id'] in plan['selection']];rows=[];error=None
        try:
            verify_artifacts()  # Charged once to the diagnostic's wall; no concurrent inference.
            for task in tasks:
                preflight();begin=time.monotonic();directory=run/task['id'];directory.mkdir()
                (directory/'task.txt').write_text(task['prompt']);shutil.copyfile(ROOT/'config/pi-bonsai-thinking-models.json',directory/'pi-models.json')
                (directory/'system-prompt.txt').write_bytes((ROOT/'config/validated-local-agent-prompt.txt').read_bytes())
                with staged_workspace(LIVE,SUITE/'tasks'/task['id']/'input',directory) as workspace:
                    cmd=client(workspace,directory/'pi-models.json',task['prompt']);(directory/'client-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
                    report=execute(directory,command(),cmd,timeout=plan['task_timeout_seconds'])
                audit=protocol(directory);grading=grade(task['id'],directory/'workspace')
                good=report['status']=='client-completed' and report['error'] is None and audit['passed']
                row={'task_id':task['id'],'category':task['category'],'utility':grading['utility'] if good else 0,'execution':report,'protocol':audit,
                     'grading':grading,'full_wall_seconds':time.monotonic()-begin}
                (directory/'scored-result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
                print(json.dumps({k:row[k] for k in ['task_id','utility','full_wall_seconds']}),flush=True)
                if report['error']:raise RuntimeError(report['error'])
                if row['utility']!=1:raise RuntimeError('original-capability-failure; remaining tasks unattempted')
        except (Exception,KeyboardInterrupt) as exc:error=str(exc) or type(exc).__name__
        finally:
            wall=time.monotonic()-started;utility=sum(row['utility'] for row in rows)
            summary={'complete':len(rows)==len(tasks) and error is None,'error':error,'utility':utility,'wall_seconds':wall,
                     'diagnostic_utility_per_hour':utility*3600/wall,'unattempted':[t['id'] for t in tasks[len(rows):]],'tasks':rows,'scope':plan['scope']}
            (run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
            (run/'sha256-recursive.json').write_text(json.dumps({str(f.relative_to(run)):digest(f) for f in run.rglob('*') if f.is_file()},indent=2)+'\n')
            print(json.dumps({k:summary[k] for k in ['complete','error','utility','wall_seconds','diagnostic_utility_per_hour','unattempted']}),flush=True)
        if error:raise SystemExit(1)


if __name__=='__main__':main()
