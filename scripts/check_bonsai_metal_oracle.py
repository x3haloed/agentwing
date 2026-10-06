#!/usr/bin/env python3
"""AW-0085 independent CPU dot oracle for tiny pinned native Metal operations."""
import ctypes
import fcntl
import json
import math
from pathlib import Path
import struct
import subprocess
from run_local_agent import ROOT, preflight, digest


def main():
    preflight()
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        original=json.loads((ROOT/'evidence/AW-0084-native-metal-compatibility.json').read_text())
        previous=Path(original['external_evidence'])
        for name,sha in original['external_files'].items():assert digest(previous/name)==sha
        for name,sha in original['dynamic_libraries'].items():assert digest(ROOT/'var/bonsai-demo/bin/mac'/name)==sha
        ref=json.loads((ROOT/'evidence/AW-0082-compiled-reference.json').read_text())
        library=Path(ref['external_evidence'])/'reference.dylib';assert digest(library)==ref['library_sha256']
        native=ctypes.CDLL(str(library));decoder=native.dequantize_row_ptq1_0;decoder.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_float),ctypes.c_int64]
        ptq=(previous/'ptq-fixture.bin').read_bytes();weights=(ctypes.c_float*(64*128))();decoder(ptq,weights,64*128)
        directory=Path('/Users/chad/Models/agentwing/evidence/AW-0085');binary=directory/'packing-metal-oracle';raw=directory/'outputs.bin'
        command=[str(binary),str(previous/'ptq-fixture.bin'),str(previous/'pq-fixture.bin'),str(raw)]
        with (directory/'native-metal.log').open('w') as log:
            result=subprocess.run(command,stdout=subprocess.PIPE,stderr=log,text=True,timeout=60)
        (directory/'native-result.json').write_text(json.dumps({'exit_code':result.returncode,'stdout':result.stdout},indent=2)+'\n')
        result.check_returncode()
        values=struct.unpack('<1024f',raw.read_bytes());metrics={}
        expected=[];outputs={'ptq':[],'pq':[]}
        for pattern in range(4):
            base=pattern*256;x=values[base:base+128]
            expected.extend(math.fsum(float(weights[row*128+j])*float(x[j]) for j in range(128)) for row in range(64))
            outputs['ptq'].extend(values[base+128:base+192]);outputs['pq'].extend(values[base+192:base+256])
        norm=math.fsum(y*y for y in expected)
        for name,actual in outputs.items():
            assert all(math.isfinite(y) for y in actual)
            diff=[a-b for a,b in zip(actual,expected)]
            metrics[name]={'relative_l2':math.sqrt(math.fsum(y*y for y in diff)/max(norm,1e-30)),
                           'maximum_absolute_difference':max(abs(y) for y in diff)}
            assert metrics[name]['relative_l2']<=1e-4
        rotated=expected[1:]+expected[:1]
        mutation=math.sqrt(math.fsum((a-b)**2 for a,b in zip(outputs['pq'],rotated))/max(norm,1e-30));assert mutation>1e-4
        evidence={'experiment':'AW-0085','passed':True,'scope':'Tiny sampled-block matrix with synthetic inputs; independent compiled CPU decode plus double-precision fsum dot oracle, not real activations or performance',
                  'output_values_each_arm':256,'metrics':metrics,'threshold_relative_l2':1e-4,'threshold_scope':'Cheap component falsifier only, not broader fidelity authority',
                  'rotated_reference_mutation_relative_l2':mutation,'rotated_reference_mutation_rejected':True,
                  'external_evidence':str(directory),'external_files':{n:digest(directory/n) for n in ['outputs.bin','native-metal.log','native-result.json','packing-metal-oracle']},
                  'native_command':command,'script_sha256':digest(Path(__file__)),
                  'native_source_sha256':digest(ROOT/'experiments/fixtures/bonsai-packing-metal-oracle.cpp'),
                  'runtime_provenance':'AW84 unchanged pinned native libraries/headers; AW82 compiled CPU decoder hash verified',
                  'fixture_provenance':'AW84 original fixture receipt verified; AW83 pinned model sampled blocks',
                  'disposition':'Retained for real projection/activation checks and complete cost measurements; no promotion'}
        print(json.dumps(evidence,indent=2))


if __name__=='__main__':main()
