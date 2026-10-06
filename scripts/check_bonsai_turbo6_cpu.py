#!/usr/bin/env python3
"""AW201 native CPU codec parity against saved4/6bit fixtures."""
import ctypes,json
from pathlib import Path
import numpy as np
from run_local_agent import digest
R=Path('/Users/chad/Models/agentwing/evidence/AW-0201');P=R.parent/'AW-0199'
def main():
 path=Path('/Users/chad/Models/agentwing/runtime-builds/prism-turbo6/bin/libggml-base.0.21.0.dylib');lib=ctypes.CDLL(str(path));ptr=ctypes.POINTER(ctypes.c_float);records=[]
 for bits in [4,6]:
  enc=getattr(lib,f'quantize_row_turbo{bits}_0_ref');enc.argtypes=[ptr,ctypes.c_void_p,ctypes.c_int64];dec=getattr(lib,f'dequantize_row_turbo{bits}_0');dec.argtypes=[ctypes.c_void_p,ptr,ctypes.c_int64]
  for layer in [3,31,63]:
   v=np.fromfile(P.parent/'AW-0185'/f'{layer}-input.bin',dtype='<f4');packed=ctypes.create_string_buffer(v.size//128*(4+16*bits));out=np.empty_like(v);enc(v.ctypes.data_as(ptr),packed,v.size);dec(packed,out.ctypes.data_as(ptr),v.size)
   inverse=lib.turbo_cpu_fwht_inverse;inverse.argtypes=[ptr,ctypes.c_int]
   for group in out.reshape(-1,128):inverse(group.ctypes.data_as(ptr),128)
   assert packed.raw==(P/f'{layer}-{bits}-packed.bin').read_bytes();assert out.tobytes()==(P/f'{layer}-{bits}-decoded.bin').read_bytes();records.append({'bits':bits,'layer':layer,'packed_and_decoded_bitexact':True})
 result={'experiment':'AW-0201','cpu_parity_passed':True,'records':records,'base_library_sha256':digest(path),'scope':'CPU codec and4bit regression parity only, no GPU or model admission'};(R/'cpu-parity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
