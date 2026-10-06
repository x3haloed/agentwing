#!/usr/bin/env python3
"""AW-0082: compare exact repacking with pinned compiled CPU decoders."""
import ctypes
import fcntl
import hashlib
import json
from pathlib import Path
import random
import subprocess
from check_bonsai_repacking_layout import SOURCE, repack
from run_local_agent import ROOT, preflight


def function(source, name):
    start = source.index('void '+name+'(')
    opening = source.index('{', start)
    depth = 1
    end = opening+1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def main():
    preflight()
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        receipt = json.loads((SOURCE/'cpu-receipt.json').read_text())
        for item in receipt:
            assert hashlib.sha256((SOURCE/item['path']).read_bytes()).hexdigest() == item['sha256']
        source = (SOURCE/'ggml/src/ggml-quants.c').read_text()
        decoders = '\n'.join(function(source, name) for name in ['dequantize_row_ptq1_0', 'dequantize_row_pq2_0'])
        prefix = '''#include <assert.h>
#include <stdint.h>
#include <string.h>
#define GGML_RESTRICT restrict
#define QK_PTQ1_0 128
#define QK_PQ2_0 128
typedef uint16_t ggml_half;
typedef struct { uint8_t qs[24]; uint8_t qh[2]; ggml_half d; } block_ptq1_0;
typedef struct { ggml_half d; uint8_t qs[32]; } block_pq2_0;
_Static_assert(sizeof(block_ptq1_0)==28, "PTQ layout");
_Static_assert(sizeof(block_pq2_0)==34, "PQ layout");
static const size_t ptq1_0_stages[3] = {16,8,1};
static float half_float(uint16_t bits) { __fp16 value; memcpy(&value,&bits,2); return (float)value; }
#define GGML_FP16_TO_FP32 half_float
'''
        suffix = '''
int equivalent(const uint8_t *a, const uint8_t *b) {
 block_ptq1_0 x; block_pq2_0 z; float y[128], w[128];
 memcpy(&x,a,28); memcpy(&z,b,34);
 dequantize_row_ptq1_0(&x,y,128); dequantize_row_pq2_0(&z,w,128);
 return memcmp(y,w,sizeof(y))==0;
}
'''
        directory = Path('/Users/chad/Models/agentwing/evidence/AW-0082/compiled-reference')
        directory.mkdir(parents=True,exist_ok=True)
        code = directory/'reference.c'; code.write_text(prefix+decoders+suffix)
        library = directory/'reference.dylib'
        cmd = ['/usr/bin/clang','-std=c11','-O2','-fno-fast-math','-dynamiclib',str(code),'-o',str(library)]
        compiled = subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        (directory/'compiler.log').write_text(compiled.stdout+compiled.stderr)
        compiled.check_returncode()
        lib = ctypes.CDLL(str(library)); lib.equivalent.argtypes=[ctypes.c_char_p,ctypes.c_char_p];lib.equivalent.restype=ctypes.c_int
        def verify(block):
            assert lib.equivalent(block,repack(block)) == 1
        count=0
        for position in range(26):
            for value in range(256):
                block=bytearray(28);block[position]=value;block[26:]=b'\x00\x3c';verify(bytes(block));count+=1
        rng=random.Random(82)
        for _ in range(128):
            block=bytes(rng.randrange(256) for _ in range(26))+b'\x00\x3c';verify(block);count+=1
        payload=bytes(range(26));scales=0
        for scale in range(65536):
            if (scale & 0x7c00)==0x7c00:continue
            verify(payload+scale.to_bytes(2,'little'));scales+=1
        original=payload+b'\x00\x3c';bad=bytearray(repack(original));bad[2]^=3
        assert lib.equivalent(original,bytes(bad)) == 0
        result={'experiment':'AW-0082','passed':True,'payload_fixtures':count,'finite_scale_patterns':scales,
                'comparison':'bitwise FP32 outputs from pinned CPU decoder functions','corrupted_code_mutation_rejected':True,
                'runtime_commit':'adfffbe41b2cabcd51fff326ab045662265062bb','source_receipt':receipt,
                'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'generated_source_sha256':hashlib.sha256(code.read_bytes()).hexdigest(),
                'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),'external_evidence':str(directory),'compiler_command':cmd,
                'compiler_version':subprocess.check_output(['/usr/bin/clang','--version'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),
                'scope':'Extracted exact CPU decoder bodies with standalone layout/half wrapper; not full runtime linkage, Metal execution, real tensors, GGUF, activations or endpoint performance',
                'disposition':'Retained for real tensor and runtime fidelity checks before full conversion'}
        print(json.dumps(result,indent=2))


if __name__=='__main__':main()
