#!/usr/bin/env python3
"""Independent local text/vision/native-tool bring-up checks; no benchmark claim."""
import shutil
import os
import fcntl
import argparse
import base64
import datetime
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
import urllib.request
import zlib
from bonsai_checkpoint_f16_server import command, verify, ROOT
from run_local_agent import host_sample, check_sample, stop_group


def request(body):
    body = {'model':'bonsai2-27b','max_tokens':768,'temperature':1.0,'top_p':0.95,
            'top_k':20,'min_p':0.05,'presence_penalty':0,'repeat_penalty':1,'frequency_penalty':0,'seed':42,'reasoning_effort':'medium',**body}
    req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions',
                                 data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    start=time.monotonic()
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req,timeout=600) as r: result=json.load(r)
    return {'request':body,'response':result,'wall_seconds':time.monotonic()-start}


def png(reverse=False):
    colors=[(255,0,0),(0,0,255)]
    if reverse: colors.reverse()
    raw=b''.join(b'\0'+b''.join(bytes(colors[x//128]) for x in range(256)) for y in range(128))
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',256,128,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')


def fixture(run,rep):
    results=[]
    def save(name,r,passed):
        r['passed']=passed
        (run/f'{name}.json').write_text(json.dumps(r,indent=2)+'\n')
        results.append({'gate':name,'passed':passed,'wall_seconds':r['wall_seconds']})
    r=request({'messages':[{'role':'user','content':'What is 17 + 25? Answer with only the integer.'}]})
    content=r['response']['choices'][0]['message'].get('content','') or ''
    content=content.strip()
    save('text',r,content=='42')
    if content!='42': raise RuntimeError('Text gate failed')
    image=png(rep%2==1);(run/'vision.png').write_bytes(image)
    r=request({'messages':[{'role':'user','content':[
        {'type':'text','text':'Name the colors of the left half and right half of this image. Answer only LEFT_COLOR, RIGHT_COLOR.'},
        {'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(image).decode()}}]}]})
    content=r['response']['choices'][0]['message'].get('content','') or ''
    content=content.lower()
    expected=['blue','red'] if rep%2==1 else ['red','blue']
    passed=all(c in content for c in expected) and content.index(expected[0])<content.index(expected[1])
    save('vision',r,passed)
    if not passed: raise RuntimeError('Vision gate failed')
    tools=[{'type':'function','function':{'name':'lookup_local_code','description':'Look up a local code by key.',
           'parameters':{'type':'object','properties':{'key':{'type':'string'}},'required':['key'],'additionalProperties':False}}}]
    messages=[{'role':'user','content':'Use lookup_local_code with key orchard. Then report the exact code returned by the tool.'}]
    r=request({'messages':messages,'tools':tools})
    msg=r['response']['choices'][0]['message']; calls=msg.get('tool_calls',[])
    valid=len(calls)==1 and calls[0]['function']['name']=='lookup_local_code'
    try: valid=valid and json.loads(calls[0]['function']['arguments'])=={'key':'orchard'}
    except (IndexError,ValueError,KeyError): valid=False
    r['tool_accounting']={'attempted':len(calls),'valid':int(valid),'productive':int(valid),'redundant':0,'malformed':int(not valid),'denied':0,'failed':0}
    save('tool-selection',r,valid)
    if not valid: raise RuntimeError('Native tool selection failed')
    code='AW62-'+hashlib.sha256(image+str(rep).encode()).hexdigest()[:10]
    messages.extend([msg,{'role':'tool','tool_call_id':calls[0]['id'],'content':code}])
    r=request({'messages':messages,'tools':tools})
    result_msg=r['response']['choices'][0]['message']
    passed=code in (result_msg.get('content') or '') and not result_msg.get('tool_calls')
    save('tool-continuation',r,passed)
    (run/'gates.json').write_text(json.dumps(results,indent=2)+'\n')
    if not passed: raise RuntimeError('Tool association/continuation failed')
    subprocess.run([sys.executable,str(ROOT/'scripts/probe_bonsai_platform_pi.py'),str(run)],check=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path);p.add_argument('--rep',type=int,default=0)
    args=p.parse_args()
    if args.fixture:
        fixture(args.fixture,args.rep);return
    found=subprocess.run(['pgrep','-f','llama-server|swiftlet-server|mlx_lm.server|ollama runner|TurboFieldfare'],capture_output=True)
    if found.returncode==0: raise RuntimeError('Another model-owning process is running')
    lock=(ROOT/'var/model-owner.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert json.loads((ROOT/'evidence/AW-0227-cost-terminal.json').read_text())['component_cost_gate_passed']
    print(verify(),flush=True)
    planpath=ROOT/'evidence/AW-0230-multimodal-plan.json'
    if planpath.exists():raise RuntimeError('Frozen plan already exists; never overwrite')
    pins={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['scripts/audit_bonsai_checkpoint_f16_admission.py','scripts/bonsai_diagnostic_protocol_bytes.py','scripts/run_bonsai_budget_debugging_v2.py','evidence/AW-0227-cost-terminal.json','evidence/AW-0226-boundary-state-terminal.json','scripts/probe_bonsai_checkpoint_f16_local.py','scripts/probe_bonsai_platform_pi.py','scripts/bonsai_checkpoint_f16_server.py','scripts/bonsai_turbo_server.py','scripts/bonsai_server.py','scripts/run_task_boundary.py','scripts/run_local_agent.py','spec/bonsai-checkpoint-f16-control.json','config/pi-bonsai-turbo-models.json','config/task-boundary.sb','node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js']}
    plan={'experiment':'AW-0230','scope':'Two full multimodal native chat/tool/Pi functional replicates, not endpoint comparison','pins':pins,'configuration':json.loads((ROOT/'spec/bonsai-checkpoint-f16-control.json').read_text()),'request_output_cap':768,'reasoning_effort':'medium','sampling':{'temperature':1,'top_p':.95,'top_k':20,'min_p':.05,'presence_penalty':0,'repeat_penalty':1},'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),'storage':'Internal SSD, uncontrolled warm OS page cache, fresh server per replicate','thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'runtime_libraries':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/Users/chad/Models/agentwing/runtime-builds/prism-gen-checkpoints-full/bin').glob('*.dylib')},'harness':'Pi0.84.4','replicates':2,'startup_timeout_seconds':180,'replicate_timeout_seconds':1800,'gates':['text42','opposite image colors in order','native tool selection and association','Pi file-tool loop','host gates','startupdisk16GiB/runtimedisk8GiB'],'stop_on_first_failure':True}
    planpath.write_text(json.dumps(plan,indent=2)+'\n')
    for rep in range(2):
        run=Path('/Users/chad/Models/agentwing/evidence/AW-0230')/datetime.datetime.now(datetime.timezone.utc).strftime(f'%Y%m%dT%H%M%SZ-rep{rep}')
        run.mkdir(parents=True)
        if shutil.disk_usage(run).free<16*1024**3:raise RuntimeError('Diskfree below16GiB startupgate')
        baseline=host_sample()[1];readings=[];server=client=None;started=time.monotonic();error=None
        cmd=command()+["--verbose"];(run/'command.json').write_text(json.dumps(cmd,indent=2)+'\n')
        (run/'thermal.txt').write_text(subprocess.check_output(['pmset','-g','therm'],text=True))
        (run/'source-hashes.json').write_text(json.dumps({str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),ROOT/'scripts/bonsai_checkpoint_f16_server.py',ROOT/'scripts/bonsai_server.py',ROOT/'spec/bonsai-checkpoint-f16-control.json',ROOT/'config/pi-bonsai-turbo-models.json',ROOT/'scripts/probe_bonsai_platform_pi.py']},indent=2)+'\n')
        (run/'plan.json').write_bytes(planpath.read_bytes())
        (run/'environment.json').write_text(json.dumps({'AGENTWING_GENERATION_CHECKPOINTS':'1'})+'\n')
        print(f'Running replicate {rep}: {run}',flush=True)
        try:
            with (run/'server.log').open('w') as log,(run/'client.log').open('w') as cl,(run/'pressure.jsonl').open('w') as pressure:
                server=subprocess.Popen(cmd,env={**os.environ,"AGENTWING_GENERATION_CHECKPOINTS":"1"},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                deadline=time.monotonic()+180;ready=False
                while not ready:
                    s=host_sample();free=shutil.disk_usage(run).free
                    if free<8*1024**3:raise RuntimeError('Diskfree below8GiB runtimegate')
                    readings.append(s);pressure.write(json.dumps({'time':time.time(),'pressure':s[0],'swap_mib':s[1],'free_bytes':free})+'\n');pressure.flush();check_sample(s,baseline)
                    if server.poll() is not None: raise RuntimeError('Server exited during load')
                    try:
                        with urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=1) as r: ready=r.status==200
                    except OSError: pass
                    if time.monotonic()>deadline: raise RuntimeError('Startup timeout')
                    time.sleep(1)
                client=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--fixture',str(run),'--rep',str(rep)],stdout=cl,stderr=subprocess.STDOUT,start_new_session=True)
                while client.poll() is None:
                    s=host_sample();free=shutil.disk_usage(run).free
                    if free<8*1024**3:raise RuntimeError('Diskfree below8GiB runtimegate')
                    readings.append(s);pressure.write(json.dumps({'time':time.time(),'pressure':s[0],'swap_mib':s[1],'free_bytes':free})+'\n');pressure.flush();check_sample(s,baseline)
                    if server.poll() is not None: raise RuntimeError('Server exited')
                    if time.monotonic()-started>1800: raise RuntimeError('Fixture timeout')
                    time.sleep(1)
                if client.returncode: raise RuntimeError(f'Fixture exited {client.returncode}')
        except (Exception,KeyboardInterrupt) as exc: error=str(exc) or type(exc).__name__
        finally:
            stop_group(client);stop_group(server)
            report={'passed':error is None,'error':error,'wall_seconds':time.monotonic()-started,'pressure_peak':max((x[0] for x in readings),default=None),'swap_growth_peak_mib':max((x[1]-baseline for x in readings),default=None),'cache_state':'cold server per replicate; OS page cache uncontrolled','scope':'Functional bring-up, not autonomous work-rate comparison'}
            (run/'result.json').write_text(json.dumps(report,indent=2)+'\n')
            hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in run.iterdir() if f.is_file()}
            (run/'sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
            print(json.dumps(report),flush=True)
        if error: raise SystemExit(1)


if __name__=='__main__': main()
