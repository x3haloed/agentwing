"""Run the unchanged original-suite grader on a disposable artifact copy."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from run_local_agent import ROOT, stop_group

SUITE = ROOT/'benchmarks/stage-a-v1'


def verify(task_id, workspace):
    tasks = json.loads((SUITE/'manifest.json').read_text())['tasks']
    if task_id not in {t['id'] for t in tasks}:
        raise ValueError('unknown original task')
    workspace = Path(workspace).resolve()
    if not workspace.is_dir() or any(p.is_symlink() for p in workspace.rglob('*')):
        return {'task_id': task_id, 'utility': 0, 'reason': 'invalid workspace or symlink'}
    with tempfile.TemporaryDirectory(prefix='agentwing-original-grade-') as tmp:
        copied = Path(tmp)/'workspace'
        shutil.copytree(workspace, copied, ignore=shutil.ignore_patterns('__pycache__', '.git'))
        command = ['/usr/bin/python3', '-I', str(ROOT/'scripts/verify_stage_a.py'),
                   '--task', task_id, '--workspace', str(copied)]
        process = subprocess.Popen(command, cwd=tmp, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=90)
            report = json.loads(stdout) if process.returncode in (0, 1) else None
            assert report is None or report['task_id'] == task_id
            return {'task_id': task_id, 'utility': int(process.returncode == 0 and report is not None and report['utility'] == 1),
                    'exit': process.returncode, 'frozen_grader_report': report,
                    'stdout': stdout[-8000:], 'stderr': stderr[-8000:]}
        except subprocess.TimeoutExpired:
            return {'task_id': task_id, 'utility': 0, 'reason': 'verifier timeout'}
        finally:
            stop_group(process)
