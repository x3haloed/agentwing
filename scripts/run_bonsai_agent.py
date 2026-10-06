#!/usr/bin/env python3
"""Run the Bonsai multimodal Pi agent on a preserved, bounded workspace copy."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from bonsai_server import ROOT, command, verify
from run_local_agent import execute, host_sample, check_sample


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check-only',action='store_true')
    p.add_argument('--workspace',type=Path)
    p.add_argument('--task-file',type=Path)
    p.add_argument('--timeout',type=int,default=900)
    p.add_argument('--image',type=Path,action='append',default=[],help='Local image attachment; repeat for multiple images')
    args=p.parse_args()
    if not args.check_only and (args.workspace is None or args.task_file is None):p.error('--workspace and --task-file required')
    lockpath=ROOT/'var/model-owner.lock';lockpath.parent.mkdir(exist_ok=True)
    with lockpath.open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if subprocess.run(['pgrep','-f','llama-server|swiftlet-server|mlx_lm.server|ollama runner|TurboFieldfare'],capture_output=True).returncode==0:
            raise RuntimeError('Another model-owning process is running')
        check_sample(host_sample(),host_sample()[1])
        print(verify(),flush=True)
        if args.check_only:return
        workspace=args.workspace.resolve(strict=True)
        if not workspace.is_dir() or workspace==workspace.parent:p.error('workspace must be a non-root directory')
        run=Path('/Users/chad/Models/agentwing/tasks')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ-bonsai')
        run.mkdir(parents=True)
        shutil.copytree(workspace,run/'workspace',symlinks=True,ignore=shutil.ignore_patterns('.git','node_modules','.venv','__pycache__','.build','build','target'))
        attachments=[]
        if args.image:
            (run/'images').mkdir()
            for index,image in enumerate(args.image):
                source=image.resolve(strict=True)
                if source.suffix.lower() not in {'.png','.jpg','.jpeg','.webp','.gif'}:p.error('Unsupported image extension')
                dest=run/'images'/f'{index}{source.suffix.lower()}'
                shutil.copy2(source,dest);attachments.append(dest)
        task=args.task_file.read_text()
        (run/'task.txt').write_text(task)
        node=os.environ.get('AGENTWING_NODE_BIN','/Users/chad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
        client=['/usr/bin/python3',str(ROOT/'scripts/run_task_boundary.py'),'--workspace',str(run/'workspace'),
                '--models-file',str(ROOT/'config/pi-bonsai-models.json'),'--',node,
                str(ROOT/'node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js'),
                '--provider','agentwing-bonsai','--model','bonsai2-27b','--thinking','medium',
                '--mode','json','--print','--no-session','--approve','--offline','--tools','bash',
                '--system-prompt',(ROOT/'config/validated-local-agent-prompt.txt').read_text().strip(),*['@'+str(image) for image in attachments],task]
        metadata={'configuration':json.loads((ROOT/'spec/bonsai-local.json').read_text()),'task_sha256':hashlib.sha256(task.encode()).hexdigest(),
                  'prompt_file_sha256':hashlib.sha256((ROOT/'config/validated-local-agent-prompt.txt').read_bytes()).hexdigest(),
                  'rendered_prompt_sha256':hashlib.sha256((ROOT/'config/validated-local-agent-prompt.txt').read_text().strip().encode()).hexdigest(),
                  'image_sha256':{image.name:hashlib.sha256(image.read_bytes()).hexdigest() for image in attachments},'timeout_seconds':args.timeout,
                  'copy_exclusions':['.git','node_modules','.venv','__pycache__','.build','build','target'],
                  'permission_policy':'workspace-state-write-local-outbound-v1'}
        (run/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
        print(f'run_dir: {run}',flush=True)
        result=execute(run,command(),client,timeout=args.timeout)
        print(json.dumps(result,indent=2))
        if result['status']!='client-completed':raise SystemExit(1)


if __name__=='__main__':main()
