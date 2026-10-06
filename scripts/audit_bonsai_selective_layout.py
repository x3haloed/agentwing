#!/usr/bin/env python3
"""Independent AW-0097 header/offset/padding audit, no payload decoding."""
import hashlib,json,struct
from pathlib import Path
from read_bonsai_tensor_directory import inspect
R=Path('/Users/chad/Models/agentwing/evidence/AW-0097')
plan=json.loads((R/'plan.json').read_text());result=json.loads((R/'result.json').read_text());assert result['passed']
source=Path('/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-PTQ1_0.gguf');candidate=Path(result['output']);a=inspect(source);b=inspect(candidate)
assert a['tensor_count']==b['tensor_count'] and a['data_offset']==b['data_offset']
with source.open('rb') as f:expected=bytearray(f.read(a['data_offset']))
with candidate.open('rb') as f:actual=f.read(b['data_offset'])
start=a['directory_end_bytes']-sum(24+len(t['name'].encode())+8*len(t['dimensions']) for t in a['tensors']);pos=start;slots={}
for t in a['tensors']:
 n=struct.unpack_from('<Q',expected,pos)[0];pos+=8;assert expected[pos:pos+n].decode()==t['name'];pos+=n+4+8*len(t['dimensions']);slots[t['name']]=(pos,pos+4);pos+=12
assert pos==a['directory_end_bytes'];ordered=sorted(a['tensors'],key=lambda t:t['relative_offset']);new={t['name']:t for t in b['tensors']};delta=0;pads=0
with source.open('rb') as src,candidate.open('rb') as dst:
 for i,t in enumerate(ordered):
  changed=t['name'] in plan['selected'];entry=new[t['name']];assert entry['dimensions']==t['dimensions'] and entry['relative_offset']==t['relative_offset']+delta
  tp,off=slots[t['name']];struct.pack_into('<Q',expected,off,entry['relative_offset'])
  if changed:struct.pack_into('<I',expected,tp,142);assert entry['type']==142
  else:assert entry['type']==t['type']
  oldsize=t['elements']//128*28 if t['type']==143 else t['elements']*{0:4,30:2}[t['type']];newsize=t['elements']//128*34 if changed else oldsize
  nextoff=ordered[i+1]['relative_offset'] if i+1<len(ordered) else a['payload_bytes'];gap=nextoff-t['relative_offset']-oldsize;assert 0<=gap<32
  src.seek(a['data_offset']+t['relative_offset']+oldsize);dst.seek(b['data_offset']+entry['relative_offset']+newsize);assert src.read(gap)==dst.read(gap);pads+=gap
  if changed:delta+=newsize-oldsize
assert bytes(expected)==actual and candidate.stat().st_size-source.stat().st_size==delta==plan['expected_expansion_bytes']
receipt={'experiment':'AW-0097','passed':True,'only_header_changes':'Selected dtype143->142 and relocated offsets; all remaining header bytes including tokenizer/metadata/alignment unchanged','all_tensor_padding_bytes_compared':pads,'tensors':len(ordered),'extra_bytes':delta,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'raw_result_sha256':hashlib.sha256((R/'result.json').read_bytes()).hexdigest()}
(R/'independent-layout-audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
