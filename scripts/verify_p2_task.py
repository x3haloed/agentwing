#!/usr/bin/env python3
"""Independent P2 grader: grade a copied workspace using the external authority."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from run_local_agent import stop_group

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / 'benchmarks/p2-v1'


def verify(task_id, workspace):
    task = next((t for t in json.loads((SUITE/'manifest.json').read_text())['tasks'] if t['id']==task_id), None)
    if task is None:
        raise ValueError('unknown task')
    workspace = Path(workspace).resolve()
    # Do not let a submitted link reach the original evidence or grader tree.
    if not workspace.is_dir() or any(p.is_symlink() for p in workspace.rglob('*')):
        return {'task_id': task_id, 'utility': 0, 'reason': 'invalid workspace or symlink'}
    with tempfile.TemporaryDirectory(prefix='agentwing-p2-grade-') as tmp:
        copied = Path(tmp)/'workspace'
        shutil.copytree(workspace, copied, ignore=shutil.ignore_patterns('__pycache__', '.git'))
        command = ['/usr/bin/python3', '-I', str(SUITE/'authorities'/task_id/'grade.py'), str(copied)]
        process = subprocess.Popen(command, cwd=tmp, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=60)
            return {'task_id': task_id, 'utility': int(process.returncode==0), 'exit': process.returncode,
                    'stdout': stdout[-8000:], 'stderr': stderr[-8000:]}
        except subprocess.TimeoutExpired:
            return {'task_id': task_id, 'utility': 0, 'reason': 'verifier timeout'}
        finally:
            stop_group(process)


def main():
    p=argparse.ArgumentParser();p.add_argument('task');p.add_argument('workspace',type=Path)
    a=p.parse_args();r=verify(a.task,a.workspace);print(json.dumps(r,indent=2));return 0 if r['utility'] else 1


if __name__=='__main__':
    raise SystemExit(main())
