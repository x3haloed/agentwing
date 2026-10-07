#!/usr/bin/env python3
"""Pinned experimental full-vision Bonsai server with six-bit cache, no speculation."""
import argparse,datetime,fcntl,json,os,subprocess,time,shutil,hashlib
from pathlib import Path
import bonsai_turbo_server as turbo
from run_local_agent import preflight,digest,host_sample,check_sample,stop_group
ROOT=turbo.ROOT
SPEC=ROOT/'spec/bonsai-checkpoint-f16-control.json'
turbo.base.SPEC=SPEC
turbo.base.BINARY=Path(json.loads(SPEC.read_text())['runtime']['server_path'])

def artifact_digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def verify():
    spec=json.loads(SPEC.read_text());runtime=spec['runtime']
    for artifact in spec['model']['artifacts']:
        p=turbo.base.WEIGHTS/artifact['filename']
        if p.stat().st_size!=artifact['bytes'] or artifact_digest(p)!=artifact['sha256']:
            raise RuntimeError('Weight integrity mismatch: '+str(p))
    for name,h in runtime['libraries'].items():
        if digest(turbo.base.BINARY.parent/name)!=h:raise RuntimeError('Library mismatch: '+name)
    if digest(turbo.base.BINARY)!=runtime['server_sha256']:raise RuntimeError('Server mismatch')
    if digest(Path(runtime['vision_cli_path']))!=runtime['vision_cli_sha256']:raise RuntimeError('Vision CLI mismatch')
    for path,h in runtime['patch_series'].items():
        if digest(ROOT/path)!=h:raise RuntimeError('Patch mismatch: '+path)
    if digest(ROOT/runtime['build_evidence'])!=runtime['build_evidence_sha256']:
        raise RuntimeError('Build receipt mismatch')
    version=subprocess.check_output([str(turbo.base.BINARY),'--version'],stderr=subprocess.STDOUT,text=True)
    if version!=runtime['version_output']:raise RuntimeError('Version banner mismatch')
    return version.strip()

def command(port=8080):
    cmd=turbo.command(port)
    cmd[cmd.index('--cache-type-k')+1]='f16'
    cmd[cmd.index('--cache-type-v')+1]='f16'
    return cmd

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8080);p.add_argument('--verify-only',action='store_true');args=p.parse_args()
    if not 1<=args.port<=65535:p.error('Invalid port')
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);print(verify(),flush=True)
        if args.verify_only:return
        preflight()
        if shutil.disk_usage(turbo.base.BINARY.parent).free<16*1024**3:raise RuntimeError('Diskfree below16GiB startup gate')
        r=Path('/Users/chad/Models/agentwing/evidence/checkpoint-f16-control-launches')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');r.mkdir(parents=True)
        cmd=command(args.port);env={**os.environ,"AGENTWING_GENERATION_CHECKPOINTS":"1"}
        (r/'launch.json').write_text(json.dumps({'command':cmd,'environment_overrides':{'AGENTWING_GENERATION_CHECKPOINTS':'1'},'profile_sha256':digest(SPEC),'harness_sha256':digest(Path(__file__))},indent=2)+'\n')
        baseline=host_sample()[1];child=None
        try:
            check_sample(host_sample(),baseline)
            with (r/'server.log').open('w') as log,(r/'pressure.jsonl').open('w') as pressure:
                child=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                print(f'Experimental Bonsai endpoint http://127.0.0.1:{args.port}; evidence {r}',flush=True)
                while child.poll() is None:
                    s=host_sample();free=shutil.disk_usage(r).free
                    if free<8*1024**3:raise RuntimeError('Diskfree below8GiB runtime gate')
                    pressure.write(json.dumps({'time':time.time(),'pressure':s[0],'swap_mib':s[1],'free_bytes':free})+'\n');pressure.flush();check_sample(s,baseline);time.sleep(1)
                if child.returncode:raise RuntimeError('Server exit '+str(child.returncode))
        finally:stop_group(child)

if __name__=='__main__':main()
