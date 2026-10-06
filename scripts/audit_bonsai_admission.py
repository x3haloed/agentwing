#!/usr/bin/env python3
"""Audit saved Bonsai admission artifacts without running a model."""
import argparse
import hashlib
import json
from pathlib import Path


def audit(run):
    hashes=json.loads((run/'sha256.json').read_text())
    for name,digest in hashes.items():
        if hashlib.sha256((run/name).read_bytes()).hexdigest()!=digest:raise ValueError(f'Hash mismatch: {name}')
    result=json.loads((run/'result.json').read_text())
    assert result['passed'] and result['pressure_peak']<4 and result['swap_growth_peak_mib']<=1024
    checks={n:json.loads((run/(n+'.json')).read_text()) for n in ['text','vision','tool-selection','tool-continuation']}
    assert checks['text']['response']['choices'][0]['message']['content'].strip()=='42'
    # Decode PNG pixels independently of the fixture generator.
    import struct,zlib
    png=(run/'vision.png').read_bytes();pos=8;compressed=b''
    while pos<len(png):
        size=struct.unpack('>I',png[pos:pos+4])[0];tag=png[pos+4:pos+8]
        if tag==b'IDAT':compressed+=png[pos+8:pos+8+size]
        pos+=size+12
    row=zlib.decompress(compressed)
    color={(255,0,0):'red',(0,0,255):'blue'}
    expected=[color[tuple(row[1:4])],color[tuple(row[1+128*3:4+128*3])]]
    observed=checks['vision']['response']['choices'][0]['message']['content'].lower()
    assert all(c in observed for c in expected) and observed.index(expected[0])<observed.index(expected[1])
    selected=checks['tool-selection']['response']['choices'][0]
    assert selected['finish_reason']=='tool_calls'
    calls=selected['message']['tool_calls'];assert len(calls)==1
    assert calls[0]['function']['name']=='lookup_local_code'
    assert json.loads(calls[0]['function']['arguments'])=={'key':'orchard'}
    continuation=checks['tool-continuation']
    reply=continuation['request']['messages'][-1]
    assert reply['role']=='tool' and reply['tool_call_id']==calls[0]['id']
    msg=continuation['response']['choices'][0]['message']
    assert reply['content'] in msg['content'] and not msg.get('tool_calls')
    assert (run/'pi-workspace/source.txt').read_bytes()==(run/'pi-workspace/answer.txt').read_bytes()
    events=[json.loads(l) for l in (run/'pi.jsonl').read_text().splitlines()]
    starts=[e for e in events if e.get('type')=='tool_execution_start']
    ends=[e for e in events if e.get('type')=='tool_execution_end']
    assert starts and len(starts)==len(ends)
    assert {e['toolCallId'] for e in starts}=={e['toolCallId'] for e in ends}
    assert all(e['toolName']=='bash' and isinstance(e['args'].get('command'),str) for e in starts)
    assert all(not e.get('isError') for e in ends)
    assert not any(e.get('message',{}).get('stopReason')=='error' for e in events if e.get('type')=='message_end')
    return {'run':str(run),'passed':True,'raw_hash_manifest_sha256':hashlib.sha256((run/'sha256.json').read_bytes()).hexdigest(),
            'wall_seconds':result['wall_seconds'],'pressure_peak':result['pressure_peak'],'swap_growth_peak_mib':result['swap_growth_peak_mib'],
            'tool_accounting':{'api':{'attempted':1,'valid':1,'productive':1,'redundant':0,'malformed':0,'denied':0,'failed':0},
                               'pi':{'attempted':len(starts),'valid':len(starts),'failed':0,'malformed':0,'denied':0,
                                     'commands':[e['args']['command'] for e in starts]}}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('runs',type=Path,nargs='+');args=p.parse_args()
    print(json.dumps([audit(run) for run in args.runs],indent=2))


if __name__=='__main__':main()
