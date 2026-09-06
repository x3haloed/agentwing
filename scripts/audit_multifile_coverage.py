#!/usr/bin/env python3
"""AW-0050 supplemental coverage evidence, separate from frozen task utility."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from run_local_agent import ROOT, digest, preflight, stop_group

MUTATION = '''
# AW-0050 diagnostic mutation in a disposable copy only.
import inspect as _aw_inspect
import functools as _aw_functools
_aw_original = list_items
_aw_signature = _aw_inspect.signature(_aw_original)
if 'include_archived' not in _aw_signature.parameters:
    raise RuntimeError('AW-0050 unsupported signature')
@_aw_functools.wraps(_aw_original)
def list_items(*args, **kwargs):
    bound = _aw_signature.bind(*args, **kwargs)
    bound.apply_defaults()
    bound.arguments['include_archived'] = False
    return _aw_original(*bound.args, **bound.kwargs)
'''

DRIVER = '''import json,os,subprocess,sys
from pathlib import Path
report={}
try:
    from ledger.api import list_items
    records=[{'id':1,'archived':True},{'id':2}]
    report={'default':list_items(records,2),'opt_in':list_items(records,2,include_archived=True),
            'input_preserved':records==[{'id':1,'archived':True},{'id':2}]}
except Exception as exc:
    report={'error':repr(exc)}
Path(os.environ['TMPDIR'],'coverage-probe.json').write_text(json.dumps(report))
raise SystemExit(subprocess.run([sys.executable,'-m','unittest','-q']).returncode)
'''


def tests(directory):
    return {str(p.relative_to(directory)): digest(p) for p in directory.rglob('test*.py') if p.is_file()}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args()
    # Exclude measured model work and share ownership discipline with its runner.
    with (ROOT/'var/local-agent.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);preflight()
        source=args.run/'dev-multi-file/workspace'
        receipt=json.loads((args.run/'sha256-recursive.json').read_text())
        def intact():
            return receipt=={str(p.relative_to(args.run)):digest(p) for p in args.run.rglob('*')
                if p.is_file() and not p.is_symlink() and p.name!='sha256-recursive.json'}
        assert intact(),'Source receipt changed or incomplete'
        assert source.is_dir() and not any(p.is_symlink() for p in source.rglob('*'))
        initial=ROOT/'benchmarks/p2-v1/tasks/dev-multi-file/input'
        base=Path('/Users/chad/Models/agentwing/evidence/AW-0050');base.mkdir(exist_ok=True)
        out=base/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(mode=0o700)
        python=shutil.which('python3');assert python
        manifest={'source_run':str(args.run),'source_receipt_sha256':digest(args.run/'sha256-recursive.json'),
            'script_sha256':digest(__file__),'python':python,'python_version':subprocess.check_output([python,'--version'],text=True),
            'boundary_sha256':digest(ROOT/'scripts/run_task_boundary.py'),
            'initial_tests':tests(initial),'submitted_tests':tests(source),
            'scope':'Supplemental copied-workspace coverage audit; no change to frozen grade or measured run clock'}
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
        started=time.monotonic();rows=[]
        for original in [False,True]:
            for mutated in [False,True]:
                name=('original-tests' if original else 'submitted-tests')+('-mutant' if mutated else '-unchanged')
                directory=out/name;directory.mkdir();workspace=directory/'workspace'
                shutil.copytree(source,workspace,ignore=shutil.ignore_patterns('__pycache__','.git'))
                if original:
                    for p in workspace.rglob('test*.py'):p.unlink()
                    for p in initial.rglob('test*.py'):
                        destination=workspace/p.relative_to(initial);destination.parent.mkdir(parents=True,exist_ok=True)
                        shutil.copyfile(p,destination)
                if mutated:
                    with (workspace/'ledger/api.py').open('a') as handle:handle.write('\n'+MUTATION)
                command=[python,str(ROOT/'scripts/run_task_boundary.py'),'--workspace',str(workspace),'--',python,'-c',DRIVER]
                (directory/'command.json').write_text(json.dumps(command,indent=2)+'\n')
                process=None;error=None;start=time.monotonic()
                with (directory/'stdout.txt').open('w') as stdout,(directory/'stderr.txt').open('w') as stderr:
                    try:
                        process=subprocess.Popen(command,stdout=stdout,stderr=stderr,start_new_session=True,
                            env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
                        process.wait(timeout=60)
                    except subprocess.TimeoutExpired:error='timeout'
                    finally:stop_group(process)
                probe=directory/'agentwing-task-state/tmp/coverage-probe.json'
                row={'case':name,'exit':process.returncode,'error':error,'seconds':time.monotonic()-start,
                    'probe':json.loads(probe.read_text()) if probe.is_file() else None}
                (directory/'result.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
        normal={'default':[{'id':2}],'opt_in':[{'id':1,'archived':True},{'id':2}],'input_preserved':True}
        mutant={'default':[{'id':2}],'opt_in':[{'id':2}],'input_preserved':True}
        targeted=all(row['probe']==(mutant if i%2 else normal) for i,row in enumerate(rows))
        evidence=targeted and all(row['error'] is None for row in rows) and [r['exit']==0 for r in rows]==[True,False,True,True]
        result={'cases':rows,'follow_up_wall_seconds':time.monotonic()-started,'targeted_mutation_verified':targeted,
            'added_archived_option_coverage_demonstrated':evidence,
            'submitted_suite_passed':rows[0]['exit']==0 and rows[0]['error'] is None,
            'test_sources_changed':manifest['submitted_tests']!=manifest['initial_tests'],
            'source_receipt_still_intact':intact(),
            'limits':['One targeted mutation is positive evidence when killed; survival does not disprove coverage of other requested behavior',
                      'Original-tests control replaces discovered test*.py files; other submitted implementation/helper files remain',
                      'Unsupported signatures, timeouts and other errors remain inconclusive; inspect logs',
                      'Frozen utility is unchanged; required prompt artifacts still need direct inspection']}
        (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
        (out/'sha256-recursive.json').write_text(json.dumps({str(p.relative_to(out)):digest(p) for p in out.rglob('*')
            if p.is_file() and not p.is_symlink() and p.name!='sha256-recursive.json'},indent=2)+'\n')
        print(json.dumps({'run':str(out),'summary':result},indent=2))
        return 0 if result['source_receipt_still_intact'] else 1


if __name__=='__main__':raise SystemExit(main())
