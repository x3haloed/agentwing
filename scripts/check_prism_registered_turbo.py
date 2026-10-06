#!/usr/bin/env python3
"""AW-0124 remapped Prism GGML traits and real KV CPU codec registration check."""
import ctypes,json,hashlib,math,struct,subprocess
from pathlib import Path
from run_local_agent import preflight,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0124');E=R.parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 preflight();baseline=host_sample();R.mkdir(exist_ok=True)
 authority=json.loads((E/'AW-0123/result.json').read_text());assert authority['passed']
 path=Path('/Users/chad/Models/agentwing/runtime-builds/prism-turbo-codec/bin/libggml-base.0.21.0.dylib');assert sha(path)==authority['libraries']['bin/libggml-base.0.21.0.dylib']['sha256']
 plan={'experiment':'AW-0124','harness_sha256':sha(__file__),'library_sha256':sha(path),'build_authority_sha256':sha(E/'AW-0123/result.json'),'packed_authority_sha256':sha(E/'AW-0110/result.json'),'capture_authority_sha256':sha(E/'AW-0109/result.json'),'acceptance':'Preserve original type42/142/143 identity; remapped144/145/146 correct names/128 block/34,50,68 bytes; all9 real192-row encoded outputs byte-identical to frozen CPU authority; canaries unchanged','scope':'Integrated Prism base traits/direct CPU codec entrypoints, not CPU attention backend or Metal/cache graph'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 lib=ctypes.CDLL(str(path));ctypes.c_int.in_dll(lib,'turbo3_cpu_wht_group_size').value=128
 lib.ggml_type_name.argtypes=[ctypes.c_int];lib.ggml_type_name.restype=ctypes.c_char_p;lib.ggml_blck_size.argtypes=[ctypes.c_int];lib.ggml_blck_size.restype=ctypes.c_int64;lib.ggml_type_size.argtypes=[ctypes.c_int];lib.ggml_type_size.restype=ctypes.c_size_t
 traits=[]
 for kind,name,block,size in [(42,'q2_0',64,18),(142,'pq2_0',128,34),(143,'ptq1_0',128,28),(144,'turbo2',128,34),(145,'turbo3',128,50),(146,'turbo4',128,68)]:
  actual={'id':kind,'name':lib.ggml_type_name(kind).decode(),'block':lib.ggml_blck_size(kind),'bytes':lib.ggml_type_size(kind)};assert actual=={'id':kind,'name':name,'block':block,'bytes':size},actual;traits.append(actual)
 import check_bonsai_attention_oracle as oracle
 oracle.CAPTURE=E/'AW-0109';tensors=oracle.read_capture();records=[];packed_authority=json.loads((E/'AW-0110/result.json').read_text())
 for bits,size in [(2,68),(3,100),(4,136)]:
  fn=getattr(lib,f'quantize_row_turbo{bits}_0_ref');fn.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_void_p,ctypes.c_int64];fn.restype=None
  for layer in [3,31,63]:
   t=tensors[layer,2];packed=bytearray()
   for head in range(4):
    for token in range(48):
     row=(ctypes.c_float*256)(*[oracle.value(t,d,token,head) for d in range(256)]);buf=ctypes.create_string_buffer(b'\xa5'*16+bytes(size)+b'\x5a'*16);fn(row,ctypes.c_void_p(ctypes.addressof(buf)+16),256);assert buf.raw[:16]==b'\xa5'*16 and buf.raw[16+size:32+size]==b'\x5a'*16;packed.extend(buf.raw[16:16+size])
   p=E/'AW-0110'/f'{layer}-turbo{bits}-v.bin';assert sha(p)==next(x['packed_value_sha256'] for x in packed_authority['records'] if x['layer']==layer and x['value_format']==f'turbo{bits}');assert bytes(packed)==p.read_bytes();records.append({'layer':layer,'bits':bits,'byte_identical':True,'canaries':True,'packed_sha256':sha(p)})
 after=host_sample();check_sample(after,baseline[1]);result={'experiment':'AW-0124','passed':len(records)==9,'traits':traits,'records':records,'phase_host_samples':[baseline,after],'plan_sha256':sha(R/'plan.json'),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
