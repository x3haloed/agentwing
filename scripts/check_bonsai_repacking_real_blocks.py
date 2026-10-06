#!/usr/bin/env python3
"""AW-0083: bounded real PTQ blocks versus compiled reference decoders."""
import ctypes
import fcntl
import hashlib
import json
from pathlib import Path
import struct
from check_bonsai_repacking_layout import repack
from read_bonsai_tensor_directory import inspect
from run_local_agent import ROOT, preflight, digest


def main():
    preflight()
    with (ROOT/'var/model-owner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        profile=json.loads((ROOT/'spec/bonsai-capacity-candidate.json').read_text())
        artifact=profile['model']['artifacts'][0]
        model=Path('/Users/chad/Models/agentwing/checkpoints/bonsai2-27b')/artifact['filename']
        assert model.stat().st_size==artifact['bytes'] and digest(model)==artifact['sha256']
        prior=json.loads((ROOT/'evidence/AW-0082-compiled-reference.json').read_text())
        library=Path(prior['external_evidence'])/'reference.dylib'
        assert digest(library)==prior['library_sha256']
        lib=ctypes.CDLL(str(library));lib.equivalent.argtypes=[ctypes.c_char_p,ctypes.c_char_p];lib.equivalent.restype=ctypes.c_int
        directory=inspect(model); tensors=[x for x in directory['tensors'] if x['type']==143]
        assert tensors and not directory['expert_named_tensors']
        raw=bytearray(); rows=[]
        with model.open('rb') as f:
            for tensor in tensors:
                assert tensor['elements']%128==0
                blocks=tensor['elements']//128
                indices=sorted({0,blocks//4,blocks//2,3*blocks//4,blocks-1})
                for index in indices:
                    offset=directory['data_offset']+tensor['relative_offset']+index*28
                    assert offset+28<=model.stat().st_size
                    f.seek(offset);block=f.read(28);assert len(block)==28
                    scale=struct.unpack('<H',block[26:])[0]
                    assert (scale & 0x7c00)!=0x7c00,'Nonfinite real scale'
                    packed=repack(block);assert lib.equivalent(block,packed)==1
                    rows.append({'tensor':tensor['name'],'dimensions':tensor['dimensions'],'block_index':index,
                                 'file_offset':offset,'source_block_sha256':hashlib.sha256(block).hexdigest(),
                                 'packed_block_sha256':hashlib.sha256(packed).hexdigest(),'scale_bits':scale})
                    raw.extend(block)
        external=Path('/Users/chad/Models/agentwing/evidence/AW-0083/real-blocks');external.mkdir(parents=True,exist_ok=True)
        fixture=external/'source-blocks.bin';fixture.write_bytes(raw)
        samples=external/'sample-manifest.json';samples.write_text(json.dumps(rows,indent=2)+'\n')
        result={'experiment':'AW-0083','passed':True,'model_revision':profile['model']['revision'],'artifact_sha256':artifact['sha256'],
                'quantized_tensors_sampled':len(tensors),'blocks_checked':len(rows),'weight_payload_bytes_sampled':len(raw),
                'scope':'Bitwise compiled CPU decoder output for bounded serialized blocks across every PTQ tensor, including early/middle/late layers and output head; no activations, routing, Metal execution or endpoint claim',
                'directory_data_offset':directory['data_offset'],'expert_named_tensors':directory['expert_named_tensors'],
                'exact_full_packing_expansion_bytes':sum(x['elements']//128*6 for x in tensors),
                'external_fixture':str(fixture),'external_fixture_sha256':digest(fixture),
                'library_sha256':prior['library_sha256'],'script_sha256':digest(Path(__file__)),
                'directory_reader_sha256':digest(ROOT/'scripts/read_bonsai_tensor_directory.py'),
                'external_sample_manifest':str(samples),'external_sample_manifest_sha256':digest(samples),
                'disposition':'Retained for full tensor-stream equivalence and real runtime/accumulated behavior checks; no candidate artifact produced'}
        print(json.dumps(result,indent=2))


if __name__=='__main__':main()
