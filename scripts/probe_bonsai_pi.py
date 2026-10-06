#!/usr/bin/env python3
"""Verify a Pi file-tool loop against the running local Bonsai endpoint."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from bonsai_server import ROOT


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    args=parser.parse_args()
    run=args.run.resolve(); workspace=run/'pi-workspace';workspace.mkdir()
    secret='LOCAL-'+hashlib.sha256(str(run).encode()).hexdigest()[:12]
    (workspace/'source.txt').write_text(secret+'\n')
    node='/Users/chad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
    cmd=['/usr/bin/python3',str(ROOT/'scripts/run_task_boundary.py'),'--workspace',str(workspace),
         '--models-file',str(ROOT/'config/pi-bonsai-models.json'),'--',node,
         str(ROOT/'node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js'),
         '--provider','agentwing-bonsai','--model','bonsai2-27b','--thinking','medium',
         '--mode','json','--print','--no-session','--approve','--offline','--tools','bash',
         '--system-prompt','Use bash to complete the task in the current directory. After verifying the output, stop.',
         'Read source.txt and copy its exact contents to answer.txt. Verify the files match.']
    with (run/'pi.jsonl').open('w') as out,(run/'pi.stderr').open('w') as err:
        result=subprocess.run(cmd,stdout=out,stderr=err,timeout=900,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    events=[json.loads(line) for line in (run/'pi.jsonl').read_text().splitlines() if line.strip()]
    attempts=[e for e in events if e.get('type')=='tool_execution_start']
    endings=[e for e in events if e.get('type')=='tool_execution_end']
    messages=[e.get('message',{}) for e in events if e.get('type')=='message_end']
    output=workspace/'answer.txt'
    correct=output.exists() and output.read_bytes()==(workspace/'source.txt').read_bytes()
    failed=sum(bool(e.get('isError')) for e in endings)
    errors=[m for m in messages if m.get('stopReason')=='error']
    passed=result.returncode==0 and correct and bool(attempts) and len(attempts)==len(endings) and not errors
    report={'passed':passed,'exit_code':result.returncode,'artifact_correct':correct,'attempted':len(attempts),
            'valid':len(attempts),'failed':failed,'denied':0,'malformed':len(errors),
            'productive':None,'redundant':None,'classification_note':'Productivity and redundancy require transcript review; no guessed counts.',
            'harness':'Pi 0.84.4','command':cmd,'prompt_sha256':hashlib.sha256(cmd[-1].encode()).hexdigest()}
    (run/'pi-result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    if not passed: raise SystemExit(1)


if __name__=='__main__':main()
