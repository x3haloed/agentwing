#!/usr/bin/env python3
"""Frozen expanded-development diagnostic for the retained Bonsai profile."""
import argparse
from collections import Counter
import datetime
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
from bonsai_generation_checkpoint_server import ROOT, command as base_command, verify as verify_artifacts
from run_local_agent import execute, preflight, digest, host_sample
from stable_workspace import staged_workspace
from verify_p2_task import SUITE, verify as grade

PLAN = ROOT/'evidence/AW-0229-development-plan.json'


def command():
    return base_command()+['--verbose']
LIVE = Path('/Users/chad/Models/agentwing/active')


from bonsai_diagnostic_protocol_bytes import protocol


def freeze():
    if PLAN.exists():raise RuntimeError('Plan exists; never overwrite frozen experiment')
    suite=json.loads((SUITE/'manifest.json').read_text())
    suite['tasks']=[t for t in suite['tasks'] if t['id']=='dev-multi-file']
    sources=['evidence/AW-0228-checkpoint-admission-terminal.json','evidence/AW-0227-cost-terminal.json','evidence/AW-0226-boundary-state-terminal.json','evidence/AW-0220-incremental-terminal.json','scripts/bonsai_diagnostic_protocol_bytes.py','scripts/audit_bonsai_checkpoint_development.py','evidence/AW-0219-incremental-prompt-hypothesis.json','evidence/AW-0218-sixth-request-terminal.json','config/bonsai-incremental-agent-prompt.txt','evidence/AW-0213-platform-admission-terminal.json','evidence/AW-0214-long-history-terminal.json','scripts/audit_bonsai_turbo6_history.py','scripts/replay_bonsai_turbo6_history.py','scripts/run_bonsai_checkpoint_multifile.py','scripts/bonsai_generation_checkpoint_server.py','scripts/bonsai_selective_server.py','scripts/audit_bonsai_selected_development.py','scripts/bonsai_server.py','scripts/run_local_agent.py','scripts/stable_workspace.py',
             'scripts/run_task_boundary.py','scripts/verify_p2_task.py','scripts/run_bonsai_budget_debugging_v2.py','scripts/audit_p2_suite.py','scripts/freeze_p2_suite.py','config/pi-bonsai-turbo-models.json',
             'config/task-boundary.sb','config/validated-local-agent-prompt.txt','spec/bonsai-local.json','spec/bonsai-generation-checkpoint-local.json','spec/validated-local-agent.json',
             'spec/p2-acceptance.json','evidence/AW-0034-corpus-freeze-v1.json','spec/bonsai-selective-packing-artifact.json','evidence/AW-0192-stationary-admission.json','evidence/AW-0191-stationary-fullserver-build.json','scripts/bonsai_turbo_server.py','scripts/audit_bonsai_stationary_full_request.py','scripts/replay_bonsai_stationary_full_request.py','scripts/audit_bonsai_rollback_full_request.py','tests/test_rollback_stream_audit.py','node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js']
    pins={p:digest(ROOT/p) for p in sources}
    pins.update({str(p.relative_to(ROOT)):digest(p) for p in SUITE.rglob('*') if p.is_file()})
    plan={'experiment':'AW-0229','protocol_version':'bounded-bash-v2','suite_kind':'p2-selected-development-falsifier','scope':'Previously exposed fixed dev-multi-file falsifier with q8-K/Turbo6-V compressed cache, AW219 incremental-execution platform prompt, AW223 generation checkpoint512/bounded2, and native non-speculative decode at16K/8192 medium; unchanged task/verifier/deadline/tool permissions/scoring, no heldout/interleaved P1 claim',
          'selection':[t['id'] for t in suite['tasks']],'successes_required':1,'stop_on_first_failure':False,
          'task_timeout_seconds':suite['default_timeout_seconds'],'startup_timeout_seconds':60,'pins':pins,
          'candidate':json.loads((ROOT/'spec/bonsai-generation-checkpoint-local.json').read_text()),'system_prompt':'config/bonsai-incremental-agent-prompt.txt',
          'thinking':'medium','tools':['bash'],'workspace_path':str(LIVE/'workspace'),'permissions':'workspace-state-write-local-outbound-v1',
          'network':'acquisition already complete; task network restricted to loopback; no benchmark authority passed to model',
          'runtime_environment':{'AGENTWING_GENERATION_CHECKPOINTS':'1'},
          'prerequisite':'AW228 full functional admission, AW227 complete interleaved component cost, and AW214 prior behavior screen must pass before launch', 'disk_policy':{'startup_minimum_free_bytes':16*1024**3,'runtime_minimum_free_bytes':8*1024**3}, 'prompt_revision':'AW219 general incremental-execution prompt; complete new harness configuration, no causal cache-only comparison. AW215/AW218 failures remain rejected; this new hypothesis does not waive their gates.'}
    PLAN.write_text(json.dumps(plan,indent=2)+'\n')


def client(workspace,models,task):
    node=json.loads((ROOT/'spec/validated-local-agent.json').read_text())['environment']['AGENTWING_NODE_BIN']
    return ['/usr/bin/python3',str(ROOT/'scripts/run_task_boundary.py'),'--workspace',str(workspace),'--models-file',str(models),'--',node,
            str(ROOT/'node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js'),'--provider','agentwing-bonsai','--model','bonsai2-27b',
            '--thinking','medium','--mode','json','--print','--no-session','--approve','--offline','--tools','bash',
            '--system-prompt',(ROOT/'config/bonsai-incremental-agent-prompt.txt').read_text().rstrip('\n'),task]


def main():
    started=time.monotonic()
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');p.add_argument('--check-only',action='store_true');args=p.parse_args()
    if args.freeze:freeze();print(f'Frozen {PLAN}');return
    plan=json.loads(PLAN.read_text())
    for path,h in plan['pins'].items():
        if digest(ROOT/path)!=h:raise RuntimeError(f'Frozen input changed: {path}')
    subprocess.run(['/usr/bin/python3',str(ROOT/'scripts/freeze_p2_suite.py')],check=True)
    preflight()
    if args.check_only:print(json.dumps({'plan_sha256':digest(PLAN),'selection':plan['selection'],'status':'pass'}));return
    assert json.loads((ROOT/'evidence/AW-0228-checkpoint-admission-terminal.json').read_text())['terminal_audit']['passed']
    assert json.loads((ROOT/'evidence/AW-0227-cost-terminal.json').read_text())['component_cost_gate_passed']
    from audit_bonsai_turbo6_history import audit as audit_request
    assert audit_request()['behavior_screen_passed']
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        root=Path('/Users/chad/Models/agentwing/evidence/AW-0229');root.mkdir(exist_ok=True)
        run=root/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');run.mkdir(mode=0o700)
        print(f'run_dir={run}',flush=True)
        record={'plan_sha256':digest(PLAN),'scope':plan['scope'],'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                'os':subprocess.check_output(['sw_vers'],text=True),'host':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),
                'storage':'internal SSD','free_bytes':shutil.disk_usage(run).free,'cache':'fresh model process per task; existing OS page cache uncontrolled',
                'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'server_command':command(),'runtime_environment':plan['runtime_environment'],'configuration':plan['candidate']}
        (run/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');(run/'plan.json').write_bytes(PLAN.read_bytes())
        for name in plan['pins']:
            snapshot=run/'source-snapshot'/name
            snapshot.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,snapshot)
        def interrupt(signum,frame):raise KeyboardInterrupt(f'signal-{signum}')
        signal.signal(signal.SIGTERM,interrupt)
        tasks=[t for t in json.loads((SUITE/'manifest.json').read_text())['tasks'] if t['id'] in plan['selection']];rows=[];error=None
        try:
            os.environ.update(plan['runtime_environment'])
            verify_artifacts()  # Charged once to the diagnostic's wall; no concurrent inference.
            for task in tasks:
                preflight();begin=time.monotonic();directory=run/task['id'];directory.mkdir()
                if shutil.disk_usage(directory).free < plan['disk_policy']['startup_minimum_free_bytes']:raise RuntimeError('startup-capacity-gate')
                def capacity_sample():
                    free=shutil.disk_usage(directory).free
                    with (directory/'capacity.jsonl').open('a') as f:f.write(json.dumps({'time':time.time(),'free_bytes':free})+'\n')
                    if free < plan['disk_policy']['runtime_minimum_free_bytes']:raise RuntimeError('runtime-capacity-gate')
                    return host_sample()
                (directory/'task.txt').write_text(task['prompt']);shutil.copyfile(ROOT/'config/pi-bonsai-turbo-models.json',directory/'pi-models.json')
                (directory/'system-prompt.txt').write_bytes((ROOT/'config/bonsai-incremental-agent-prompt.txt').read_bytes())
                with staged_workspace(LIVE,SUITE/'tasks'/task['id']/'input',directory) as workspace:
                    cmd=client(workspace,directory/'pi-models.json',task['prompt']);(directory/'client-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
                    report=execute(directory,command(),cmd,timeout=plan['task_timeout_seconds'],sample=capacity_sample)
                audit=protocol(directory);grading=grade(task['id'],directory/'workspace')
                good=report['status']=='client-completed' and report['error'] is None and audit['passed']
                row={'task_id':task['id'],'category':task['category'],'utility':grading['utility'] if good else 0,'execution':report,'protocol':audit,
                     'grading':grading,'full_wall_seconds':time.monotonic()-begin}
                (directory/'scored-result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
                print(json.dumps({k:row[k] for k in ['task_id','utility','full_wall_seconds']}),flush=True)
                if report['error']:raise RuntimeError(report['error'])
                if not audit['passed']:raise RuntimeError('protocol-or-history-integrity-failure; remaining tasks unattempted')
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
