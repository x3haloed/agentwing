#!/usr/bin/env python3
"""AW-0097 exact selective GGUF build and whole-payload integrity audit."""
import ctypes,fcntl,hashlib,json,os,struct,subprocess,threading,time
from pathlib import Path
from read_bonsai_tensor_directory import inspect
from run_local_agent import ROOT,preflight,digest,host_sample,check_sample
R=Path('/Users/chad/Models/agentwing/evidence/AW-0097')
SOURCE=Path('/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-PTQ1_0.gguf')
OUTPUT=SOURCE.with_name('Ternary-Bonsai-2-27B-attention-PQ2_0.gguf')
CHUNK=28*65536

def main():
 preflight()
 with (ROOT/'var/model-owner.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  spec=json.loads((ROOT/'spec/bonsai-selective-packing-candidate.json').read_text());directory=inspect(SOURCE)
  import re
  selected={t['name'] for t in directory['tensors'] if re.fullmatch(spec['tensor_selector_regex'],t['name'])};assert len(selected)==64
  converter=Path('/Users/chad/Models/agentwing/evidence/AW-0086/repack.dylib');assert digest(converter)=='c1a0409f59334d35bfd08ad5362bee4f56bad24f065b3fbd42f0b9cb2ca54784'
  pack=ctypes.CDLL(str(converter)).repack_ptq_blocks;pack.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];pack.restype=ctypes.c_int
  verify=ctypes.CDLL(str(R/'lut-verifier.dylib')).verify_ptq_pq;verify.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_size_t];verify.restype=ctypes.c_int
  fixture=Path('/Users/chad/Models/agentwing/evidence/AW-0083/real-blocks/source-blocks.bin').read_bytes();q=ctypes.create_string_buffer(len(fixture)//28*34);assert pack(fixture,len(fixture),q,len(q))==1;assert verify(fixture,len(fixture),q.raw,len(q))==1
  mutation=bytearray(q.raw);mutation[2]^=1;assert verify(fixture,len(fixture),bytes(mutation),len(q))==0;mutation=bytearray(q.raw);mutation[0]^=1;assert verify(fixture,len(fixture),bytes(mutation),len(q))==0
  plan={'experiment':'AW-0097','candidate_spec_sha256':digest(ROOT/'spec/bonsai-selective-packing-candidate.json'),'source_sha256':spec['base_model_sha256'],'script_sha256':digest(Path(__file__)),'directory_reader_sha256':digest(ROOT/'scripts/read_bonsai_tensor_directory.py'),'verifier_source_sha256':digest(ROOT/'experiments/fixtures/bonsai-repack-lut-verifier.cpp'),'converter_sha256':digest(converter),'verifier_sha256':digest(R/'lut-verifier.dylib'),'selected':sorted(selected),'chunk_bytes':CHUNK,'expected_expansion_bytes':spec['expected_payload_expansion_bytes'],'acceptance':'All changed decoded codes/raw scales exact via independent Metal LUT; all unchanged tensor bytes/padding equal; complete metadata/tokenizer bytes preserved; host gates','fixture_blocks':len(fixture)//28,'negative_code_and_scale_detected':True,'output':str(OUTPUT),'storage':'Internal SSD; warm/uncontrolled OS page cache; fsync requested, no cold I/O claim','hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'os':subprocess.check_output(['sw_vers'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True)}
  assert not (R/'plan.json').exists() and not OUTPUT.exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
  baseline=host_sample()[1];samples=[];errors=[];stop=threading.Event()
  def monitor():
   while not stop.is_set():
    try:
     s=host_sample();samples.append(s);check_sample(s,baseline)
     with (R/'pressure.tsv').open('a') as f:f.write(f'{time.time()}\t{s[0]}\t{s[1]}\n')
    except Exception as exc:errors.append(str(exc));return
    stop.wait(.25)
  thread=threading.Thread(target=monitor);thread.start()
  def gate():
   if errors:raise RuntimeError(errors[0])
  def streamhash(path):
   sha=hashlib.sha256()
   with path.open('rb') as f:
    for b in iter(lambda:f.read(8*1024*1024),b''):gate();sha.update(b)
   return sha.hexdigest()
  timings={};records=[];error=None;start=time.monotonic();partial=OUTPUT.with_suffix('.gguf.partial')
  try:
   assert streamhash(SOURCE)==spec['base_model_sha256'];timings['source_hash_seconds']=time.monotonic()-start
   with SOURCE.open('rb') as f:header=bytearray(f.read(directory['data_offset']))
   begin=directory['directory_end_bytes']-sum(8+len(t['name'].encode())+4+8*len(t['dimensions'])+4+8 for t in directory['tensors']);pos=begin;slots={}
   for t in directory['tensors']:
    length=struct.unpack_from('<Q',header,pos)[0];pos+=8;assert header[pos:pos+length].decode()==t['name'];pos+=length
    ndim=struct.unpack_from('<I',header,pos)[0];pos+=4;assert ndim==len(t['dimensions']);pos+=8*ndim
    assert struct.unpack_from('<I',header,pos)[0]==t['type'];slots[t['name']]=(pos,pos+4);pos+=12
   assert pos==directory['directory_end_bytes']
   ordered=sorted(directory['tensors'],key=lambda t:t['relative_offset']);delta=0
   for t in ordered:
    tp,off=slots[t['name']];struct.pack_into('<Q',header,off,t['relative_offset']+delta)
    if t['name'] in selected:assert t['type']==143;struct.pack_into('<I',header,tp,142);delta+=t['elements']//128*6
   assert delta==spec['expected_payload_expansion_bytes'];begin_write=time.monotonic()
   with SOURCE.open('rb') as src,partial.open('xb') as dst:
    dst.write(header);src.seek(directory['data_offset'])
    for i,t in enumerate(ordered):
     gate();assert src.tell()==directory['data_offset']+t['relative_offset']
     size=t['elements']*({0:4,30:2}[t['type']]) if t['type']!=143 else t['elements']//128*28
     remaining=size;original=hashlib.sha256();converted=hashlib.sha256()
     while remaining:
      data=src.read(min(CHUNK,remaining));assert data;remaining-=len(data);original.update(data)
      if t['name'] in selected:
       q=ctypes.create_string_buffer(len(data)//28*34);assert pack(data,len(data),q,len(q))==1;output=q.raw;assert verify(data,len(data),output,len(output))==1
      else:output=data
      dst.write(output);converted.update(output);gate()
     records.append({'name':t['name'],'changed':t['name'] in selected,'source_payload_sha256':original.hexdigest(),'candidate_payload_sha256':converted.hexdigest()})
     next_offset=ordered[i+1]['relative_offset'] if i+1<len(ordered) else directory['payload_bytes'];gap=next_offset-t['relative_offset']-size;assert 0<=gap<32;dst.write(src.read(gap))
    dst.flush();flush=time.monotonic();os.fsync(dst.fileno());timings['fsync_seconds']=time.monotonic()-flush
   timings['write_conversion_fsync_seconds']=time.monotonic()-begin_write
   assert partial.stat().st_size==SOURCE.stat().st_size+delta;candidate=inspect(partial);assert candidate['tensor_count']==directory['tensor_count']
   with partial.open('rb') as f:assert f.read(begin)==bytes(header[:begin])
   verify_start=time.monotonic()
   with SOURCE.open('rb') as src,partial.open('rb') as dst:
    old={t['name']:t for t in directory['tensors']}
    for t in candidate['tensors']:
     original=old[t['name']];assert t['dimensions']==original['dimensions'];assert t['type']==(142 if t['name'] in selected else original['type']);src.seek(directory['data_offset']+original['relative_offset']);dst.seek(candidate['data_offset']+t['relative_offset']);remaining=original['elements']//128*28 if original['type']==143 else original['elements']*{0:4,30:2}[original['type']]
     while remaining:
      data=src.read(min(CHUNK,remaining));assert data;remaining-=len(data)
      q=dst.read(len(data)//28*34 if t['name'] in selected else len(data));assert verify(data,len(data),q,len(q))==1 if t['name'] in selected else data==q;gate()
   timings['disk_reverification_seconds']=time.monotonic()-verify_start;output_sha=streamhash(partial);gate();os.rename(partial,OUTPUT)
   (R/'tensor-integrity.json').write_text(json.dumps(records,indent=2)+'\n')
  except Exception as exc:error=str(exc) or type(exc).__name__;output_sha=None
  finally:
   stop.set();thread.join();timings['full_build_audit_seconds']=time.monotonic()-start
   result={'experiment':'AW-0097','passed':error is None and OUTPUT.exists(),'error':error,'output':str(OUTPUT),'output_sha256':output_sha,'output_bytes':OUTPUT.stat().st_size if OUTPUT.exists() else None,'selected_tensors':len(selected),'unchanged_tensors':len(directory['tensors'])-len(selected),'timings':timings,'pressure_peak':max(s[0] for s in samples),'swap_growth_peak_mib':max(0,max(s[1] for s in samples)-baseline),'plan_sha256':digest(R/'plan.json'),'tensor_integrity_sha256':digest(R/'tensor-integrity.json') if (R/'tensor-integrity.json').exists() else None,'external_evidence':str(R),'scope':'Serialized artifact/code/scale integrity and warm build cost, not runtime loading/activation/behavior or endpoint improvement'}
   (R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
