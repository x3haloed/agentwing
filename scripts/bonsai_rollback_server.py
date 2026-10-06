#!/usr/bin/env python3
"""Pinned experimental full-vision Bonsai server with bounded ngram rollback."""
import argparse,datetime,fcntl,json,os,subprocess,time
from pathlib import Path
import bonsai_turbo_server as turbo
from run_local_agent import preflight,digest,host_sample,check_sample,stop_group
ROOT=turbo.ROOT
SPEC=ROOT/'spec/bonsai-turbo-rollback-local.json'
turbo.base.SPEC=SPEC
turbo.base.BINARY=Path(json.loads(SPEC.read_text())['runtime']['server_path'])

def verify():
    spec=json.loads(SPEC.read_text());runtime=spec['runtime']
    for artifact in spec['model']['artifacts']:
        p=turbo.base.WEIGHTS/artifact['filename']
        if p.stat().st_size!=artifact['bytes'] or digest(p)!=artifact['sha256']:
            raise RuntimeError('Weight integrity mismatch: '+str(p))
    for name,h in runtime['libraries'].items():
        if digest(turbo.base.BINARY.parent/name)!=h:raise RuntimeError('Library mismatch: '+name)
    if digest(turbo.base.BINARY)!=runtime['server_sha256']:raise RuntimeError('Server mismatch')
    for path,h in runtime['patch_series'].items():
        if digest(ROOT/path)!=h:raise RuntimeError('Patch mismatch: '+path)
    if digest(ROOT/runtime['build_evidence'])!=runtime['build_evidence_sha256']:
        raise RuntimeError('Build receipt mismatch')
    version=subprocess.check_output([str(turbo.base.BINARY),'--version'],stderr=subprocess.STDOUT,text=True)
    if version!=runtime['version_output']:raise RuntimeError('Version banner mismatch')
    return version.strip()

def command(port=8080):
    s=json.loads(SPEC.read_text())['speculation']
    return turbo.command(port)+['--spec-type',s['type'],'--spec-ngram-simple-size-n',str(s['lookup']),
                                '--spec-ngram-simple-size-m',str(s['proposal'])]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8080);p.add_argument('--verify-only',action='store_true');args=p.parse_args()
    if not 1<=args.port<=65535:p.error('Invalid port')
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);print(verify(),flush=True)
        if args.verify_only:return
        preflight()
        r=Path('/Users/chad/Models/agentwing/evidence/rollback-launches')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');r.mkdir(parents=True)
        cmd=command(args.port);env=os.environ.copy();env.update(json.loads(SPEC.read_text())['speculation']['environment'])
        (r/'launch.json').write_text(json.dumps({'command':cmd,'environment_overrides':json.loads(SPEC.read_text())['speculation']['environment'],'profile_sha256':digest(SPEC),'harness_sha256':digest(Path(__file__))},indent=2)+'\n')
        baseline=host_sample()[1];child=None
        try:
            check_sample(host_sample(),baseline)
            with (r/'server.log').open('w') as log,(r/'pressure.jsonl').open('w') as pressure:
                child=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                print(f'Experimental Bonsai endpoint http://127.0.0.1:{args.port}; evidence {r}',flush=True)
                while child.poll() is None:
                    s=host_sample();pressure.write(json.dumps({'time':time.time(),'pressure':s[0],'swap_mib':s[1]})+'\n');pressure.flush();check_sample(s,baseline);time.sleep(1)
                if child.returncode:raise RuntimeError('Server exit '+str(child.returncode))
        finally:stop_group(child)

if __name__=='__main__':main()
