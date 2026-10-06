#!/usr/bin/env python3
"""AW-0086 bounded full real projection shapes; no agent performance claim."""
import ctypes
import fcntl
import json
import math
from pathlib import Path
import signal
import struct
import subprocess
import time
from read_bonsai_tensor_directory import inspect
from run_local_agent import ROOT, preflight, digest, host_sample, check_sample


def main():
    preflight()
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        root=Path('/Users/chad/Models/agentwing/evidence/AW-0086')
        selection=['blk.0.ffn_up.weight','blk.31.ffn_up.weight','blk.63.ffn_up.weight']
        sources=['experiments/fixtures/bonsai-exact-repack.cpp','experiments/fixtures/bonsai-real-projection-metal.cpp',
                 'scripts/check_bonsai_real_projection_metal.py','scripts/read_bonsai_tensor_directory.py']
        plan={'selection':selection,'patterns':['ones','alternating','sine','one-hot'],'sampled_cpu_rows':32,
              'relative_l2_limit':1e-4,'limit_scope':'Cheap component falsifier, not model fidelity acceptance',
              'native_timeout_seconds':150,'source_hashes':{p:digest(ROOT/p) for p in sources},
              'native_binary_sha256':digest(root/'real-projection-metal'),'repack_library_sha256':digest(root/'repack.dylib')}
        planpath=root/'projection-plan.json'
        if planpath.exists():raise RuntimeError('Frozen plan already exists; preserve original run')
        planpath.write_text(json.dumps(plan,indent=2)+'\n')
        original=json.loads((ROOT/'evidence/AW-0084-native-metal-compatibility.json').read_text())
        for n,h in original['dynamic_libraries'].items():assert digest(ROOT/'var/bonsai-demo/bin/mac'/n)==h
        nativecheck=json.loads((root/'native-repacker-check.json').read_text());assert nativecheck['library_sha256']==plan['repack_library_sha256']
        ref=json.loads((ROOT/'evidence/AW-0082-compiled-reference.json').read_text());library=Path(ref['external_evidence'])/'reference.dylib';assert digest(library)==ref['library_sha256']
        cpu=ctypes.CDLL(str(library));decoder=cpu.dequantize_row_ptq1_0;decoder.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_float),ctypes.c_int64]
        pack=ctypes.CDLL(str(root/'repack.dylib')).repack_ptq_blocks;pack.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];pack.restype=ctypes.c_int
        model=Path('/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-PTQ1_0.gguf')
        artifact=json.loads((ROOT/'spec/bonsai-capacity-candidate.json').read_text())['model']['artifacts'][0]
        baseline=host_sample()[1];samples=[]
        def sample():
            current=host_sample();check_sample(current,baseline);samples.append(current)
            with (root/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{current[0]}\t{current[1]}\n')
        sample();assert digest(model)==artifact['sha256'];directory=inspect(model);sample()
        records=[];error=None
        try:
            with model.open('rb') as weights:
                for name in selection:
                    t=next(x for x in directory['tensors'] if x['name']==name);assert t['type']==143
                    width,rows=t['dimensions'];assert width%128==0
                    case=root/name;case.mkdir();size=t['elements']//128*28
                    weights.seek(directory['data_offset']+t['relative_offset']);data=weights.read(size);assert len(data)==size
                    packed=ctypes.create_string_buffer(size//28*34);assert pack(data,size,packed,len(packed))==1
                    (case/'ptq.bin').write_bytes(data);(case/'pq.bin').write_bytes(packed.raw);sample()
                    command=[str(root/'real-projection-metal'),str(case/'ptq.bin'),str(case/'pq.bin'),str(case/'outputs.bin'),str(width),str(rows)]
                    with (case/'stdout.log').open('w') as out,(case/'native.log').open('w') as err:
                        proc=subprocess.Popen(command,stdout=out,stderr=err,start_new_session=True);started=time.monotonic()
                        try:
                            while proc.poll() is None:
                                sample()
                                if time.monotonic()-started>150:raise RuntimeError('native-timeout')
                                time.sleep(.2)
                        finally:
                            if proc.poll() is None:signal.signal(signal.SIGTERM,signal.SIG_DFL);import os;os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                    assert proc.returncode==0,'Native projection failure'
                    mutual=json.loads((case/'stdout.log').read_text());raw=(case/'outputs.bin').read_bytes()
                    assert len(raw)==4*(width+2*rows)*4
                    values=struct.unpack('<'+str(len(raw)//4)+'f',raw);chosen=sorted({i*(rows-1)//31 for i in range(32)})
                    expected=[];actual={'ptq':[],'pq':[]}
                    for pattern in range(4):
                        base=pattern*(width+2*rows);x=values[base:base+width]
                        for row in chosen:
                            block=data[row*(width//128)*28:(row+1)*(width//128)*28];decoded=(ctypes.c_float*width)();decoder(block,decoded,width)
                            expected.append(math.fsum(float(decoded[j])*float(x[j]) for j in range(width)))
                            actual['ptq'].append(values[base+width+row]);actual['pq'].append(values[base+width+rows+row])
                    norm=math.fsum(x*x for x in expected);metrics={}
                    for arm,a in actual.items():
                        relative=math.sqrt(math.fsum((x-y)**2 for x,y in zip(a,expected))/max(norm,1e-30));assert relative<=1e-4
                        metrics[arm]={'relative_l2':relative,'maximum_absolute_difference':max(abs(x-y) for x,y in zip(a,expected))}
                    record={'tensor':name,'dimensions':t['dimensions'],'ptq_bytes':size,'pq_bytes':len(packed),'mutual':mutual,'cpu_oracle_rows':chosen,'cpu_metrics':metrics,
                            'files':{p.name:digest(p) for p in case.iterdir() if p.is_file()}}
                    records.append(record);print(json.dumps({'tensor':name,'passed':True,'cpu_metrics':metrics}),flush=True);sample()
        except Exception as exc:error=str(exc) or type(exc).__name__
        finally:
            result={'experiment':'AW-0086','passed':len(records)==3 and error is None,'error':error,'plan_sha256':digest(planpath),
                    'model_sha256':artifact['sha256'],'runtime_commit':'adfffbe41b2cabcd51fff326ab045662265062bb',
                    'scope':'Full real serialized projection shapes with synthetic inputs; no captured activations, Hadamard application, accumulated model behavior or speed claim',
                    'pressure_peak':max(x[0] for x in samples),'swap_growth_peak_mib':max(0,max(x[1] for x in samples)-baseline),'records':records,
                    'os':subprocess.check_output(['sw_vers'],text=True),'host':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),
                    'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'external_evidence':str(root),'native_repacker_check':nativecheck,
                    'disposition':'Retained for captured activation fidelity and complete cost screening' if error is None else 'Rejected pending failure analysis'}
            (root/'projection-result.json').write_text(json.dumps(result,indent=2)+'\n')
        if error:raise SystemExit(error)


if __name__=='__main__':main()
