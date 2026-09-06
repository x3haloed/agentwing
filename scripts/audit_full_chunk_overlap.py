#!/usr/bin/env python3
"""AW-0043 accumulated bit-pattern, trajectory and historical coverage audit."""
from collections import Counter
import contextlib
import io
import json
from pathlib import Path
import struct
import sys
from audit_chunk_overlap import main as audit_runtime, digest

def main():
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):status=audit_runtime()
    result=json.loads(capture.getvalue());run=Path(result['run']);assert status==0
    prior=Path('/Users/chad/Models/agentwing/evidence/AW-0031/20260905T183732Z')
    admitted=Path('/Users/chad/Models/agentwing/evidence/AW-0037/20260906T063224.469387Z')
    for root in [prior,admitted]:
        for rel,h in json.loads((root/'sha256.json').read_text()).items():assert digest(root/rel)==h,rel
    old_counts=Counter((r['layer'],e) for r in map(json.loads,(prior/'T1/experts.jsonl').read_text().splitlines()) if r['event']=='route' for e in r['experts'])
    old_fixtures={(r['layer'],e) for r in json.loads((admitted/'fixtures.json').read_text()) for e in r['experts']};assert len(old_fixtures)==250
    records_total=0
    for case,data in result['cases'].items():
        all_records=[]
        for arm in ['C1','A1','C2']:
            root=run/(case+'-'+arm)
            rows=[json.loads(x) for x in (root/'activations.jsonl').read_text().splitlines()]
            assert 0<len(rows)<=30 and [r['sequence'] for r in rows]==list(range(len(rows)))
            assert {(r['layer'],r['schedule_layer_ordinal']) for r in rows if r['schedule']=='single-token'}=={(layer,n) for layer in [0,20,39] for n in [0,7,15,31,47,63]},'Missing declared later decode checkpoints'
            routes=[json.loads(x) for x in (root/'routes.jsonl').read_text().splitlines()];by_layer={i:[] for i in range(40)}
            for r in routes:
                if r['event']=='route':by_layer[r['layer']].append(r['experts'])
            for r in rows:
                assert r['layer'] in [0,20,39] and len(r['input_f32_bits'])==2048 and len(r['weights_f32_bits'])==8
                assert by_layer[r['layer']][r['position']]==r['experts']
                for field in ['input_f32_bits','weights_f32_bits']:
                    assert all(type(b) is int and 0<=b<2**32 and b&0x7f800000!=0x7f800000 for b in r[field])
                weights=[struct.unpack('<f',struct.pack('<I',b))[0] for b in r['weights_f32_bits']]
                assert all(w>=0 for w in weights) and abs(sum(weights)-1)<1e-5
            all_records.append(rows);records_total+=len(rows)
        assert all_records[0]==all_records[1]==all_records[2],'Accumulated activation or weight discrepancy'
        routes=[json.loads(x) for x in (run/(case+'-A1')/'routes.jsonl').read_text().splitlines()]
        identities={(r['layer'],e) for r in routes if r['event']=='route' for e in r['experts']}
        sampled={(r['layer'],e) for r in all_records[1] for e in r['experts']}
        data['activation_records_per_arm']=len(all_records[1]);data['activation_bit_patterns_match']=True
        data['coverage']={'full_route_distinct_identities':len(identities),'new_relative_to_aw0036_fixtures':len(identities-old_fixtures),'absent_from_aw0031_trace':len(identities-set(old_counts)),'seen_once_or_twice_in_aw0031':sum(1<=old_counts[k]<=2 for k in identities),'captured_distinct_identities':len(sampled),'captured_new_relative_to_aw0036':len(sampled-old_fixtures),'captured_absent_from_aw0031':len(sampled-set(old_counts)),'captured_seen_once_or_twice_in_aw0031':sum(1<=old_counts[k]<=2 for k in sampled)}
        assert data['coverage']['captured_new_relative_to_aw0036']>0 and data['coverage']['captured_absent_from_aw0031']+data['coverage']['captured_seen_once_or_twice_in_aw0031']>0
    result['activation_records_all_arms']=records_total
    result['historical_receipts']={str(root):digest(root/'sha256.json') for root in [prior,admitted]}
    result['limits']=['Two development prompts with 64 generated tokens each; not autonomous tasks or universal capability','Historical rarity is defined only relative to AW-0031; fixture novelty is relative to 250 AW-0036 identities','Common activation observer and incomplete overlapped phase attribution; timing remains diagnostic','No held-out task exposure or promotion']
    print(json.dumps(result,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
