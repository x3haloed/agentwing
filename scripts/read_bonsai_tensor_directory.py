#!/usr/bin/env python3
"""Read bounded GGUF metadata and return tensor payload locations."""
import argparse
from collections import Counter
import json
from pathlib import Path
import struct

FORMATS={0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}
LIMIT=32*1024*1024


def inspect(path):
    path=path.resolve();size=path.stat().st_size
    with path.open('rb') as f:
        def unpack(fmt):
            n=struct.calcsize('<'+fmt);data=f.read(n)
            if len(data)!=n:raise ValueError('Truncated GGUF directory')
            if f.tell()>LIMIT:raise ValueError('Metadata exceeds bounded inspection limit')
            return struct.unpack('<'+fmt,data)[0]
        def string():
            n=unpack('Q')
            if f.tell()+n>LIMIT:raise ValueError('Oversized GGUF metadata string')
            data=f.read(n)
            if len(data)!=n:raise ValueError('Truncated GGUF string')
            return data.decode('utf-8')
        def value(kind,keep=True):
            if kind in FORMATS:return unpack(FORMATS[kind])
            if kind==8:return string()
            if kind==9:
                subtype=unpack('I');count=unpack('Q')
                if count>1000000:raise ValueError('Oversized metadata array')
                if subtype in FORMATS and not keep:
                    f.seek(struct.calcsize('<'+FORMATS[subtype])*count,1)
                    if f.tell()>LIMIT:raise ValueError('Metadata exceeds bounded limit')
                    return {'array_elements':count}
                for _ in range(count):value(subtype,False)
                return {'array_elements':count}
            raise ValueError(f'Unknown GGUF metadata kind {kind}')
        if f.read(4)!=b'GGUF':raise ValueError('Not a GGUF artifact')
        version=unpack('I');assert version==3
        tensors=unpack('Q');pairs=unpack('Q');assert tensors<100000 and pairs<100000
        metadata={}
        for _ in range(pairs):
            key=string();kind=unpack('I');item=value(kind,not key.startswith('tokenizer.'))
            if not key.startswith('tokenizer.'):metadata[key]=item
        names=[];types=Counter();elements=0;expert_names=[];offsets=[];records=[]
        for _ in range(tensors):
            name=string();ndim=unpack('I');assert 1<=ndim<=4
            dims=[unpack('Q') for _ in range(ndim)];dtype=unpack('I');offset=unpack('Q')
            count=1
            for n in dims:count*=n
            elements+=count;names.append(name);types[dtype]+=1;offsets.append(offset)
            records.append({"name":name,"dimensions":dims,"elements":count,"type":dtype,"relative_offset":offset})
            if 'exps' in name or 'expert' in name or 'ffn_gate_inp' in name:expert_names.append(name)
        alignment=metadata.get('general.alignment',32)
        data_offset=(f.tell()+alignment-1)//alignment*alignment
        assert data_offset<=size and all(o<size-data_offset for o in offsets)
        return {'path':str(path),'file_bytes':size,'gguf_version':version,'metadata_pairs':pairs,'tensor_count':tensors,
                'logical_tensor_elements':elements,'directory_end_bytes':f.tell(),'alignment_padding_bytes':data_offset-f.tell(),
                'data_offset':data_offset,'tensors':records,'payload_bytes':size-data_offset,'tensor_types':dict(types),'expert_named_tensors':expert_names,
                'architecture':metadata.get('general.architecture'),'metadata':metadata,
                'scope':'Static serialized layout evidence; no decode cost, residency, numeric fidelity, route behavior or endpoint utility measured.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('paths',type=Path,nargs='+');a=p.parse_args()
    print(json.dumps([inspect(path) for path in a.paths],indent=2))


if __name__=='__main__':main()
