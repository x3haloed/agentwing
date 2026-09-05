"""Audit AW-0031 traces and simulate cache capacities on fixed actual routes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def simulate(batches, capacity):
    keys=[];lookup={};freq=Counter();uses=[];ticks=0;hits=misses=0;per_phase={'prefill':[0,0],'decode':[0,0]}
    for i,row in enumerate(batches):
        ticks+=1;protected=set();phase='prefill' if i<40 else 'decode'
        for expert in row['experts']:
            key=(row['layer'],expert);freq[key]+=1
            if key in lookup:
                slot=lookup[key];hits+=1;per_phase[phase][0]+=1
            else:
                misses+=1;per_phase[phase][1]+=1
                if len(keys)<capacity:
                    slot=len(keys);keys.append(key);uses.append(ticks)
                else:
                    slot=min((j for j in range(capacity) if j not in protected),key=lambda j:(freq[keys[j]],uses[j],j))
                    del lookup[keys[slot]];keys[slot]=key
                lookup[key]=slot
            uses[slot]=ticks;protected.add(slot)
    return {'capacity':capacity,'hits':hits,'misses':misses,'per_phase_hits_misses':per_phase,'logical_miss_GiB':misses*3342336/2**30}


def main():
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);args=p.parse_args();run=args.run
    for name,h in json.loads((run/'sha256.json').read_text()).items():
        assert hashlib.sha256((run/name).read_bytes()).hexdigest()==h,name
    rows=[json.loads(x) for x in (run/'T1/experts.jsonl').read_text().splitlines()]
    assert [x['sequence'] for x in rows]==list(range(len(rows))) and len(rows)<10000
    routes=[r for r in rows if r['event']=='route'];batches=[r for r in rows if r['event']=='fetch']
    assert len(routes)==53*40 and Counter(r['layer'] for r in routes)==Counter({i:53 for i in range(40)})
    assert len(batches)==25*40
    # This diagnostic is29 prompt tokens followed by24 decode steps; within each
    # layer, routing observer invocations retain token order under both schedules.
    by_layer={i:[] for i in range(40)}
    for r in routes:by_layer[r['layer']].append(r['experts'])
    assert all(len(e)==8 and len(set(e))==8 for routes_l in by_layer.values() for e in routes_l)
    for i,r in enumerate(batches):
        layer=r['layer']
        if i<40:assert set(r['experts'])==set(e for es in by_layer[layer][:29] for e in es)
        else:
            decode=(i-40)//40;assert r['experts']==by_layer[layer][29+decode]
        assert set(r['misses']).issubset(r['experts'])
        assert r['logical_bytes']==len(r['misses'])*3342336
    observed={'hits':sum(len(r['experts'])-len(r['misses']) for r in batches),'misses':sum(len(r['misses']) for r in batches)}
    sims=[simulate(batches,c) for c in [160,240,320,480]]
    assert {k:sims[0][k] for k in ['hits','misses']}==observed
    step_sets=[{(layer,e) for layer in range(40) for e in by_layer[layer][t]} for t in range(29,53)]
    overlap=[len(a&b) for a,b in zip(step_sets,step_sets[1:])]
    arms=[]
    for arm in ['C1','T1','C2']:
        io=[json.loads(x) for x in (run/arm/'io.jsonl').read_text().splitlines()]
        log=(run/arm/'stderr.txt').read_text();metrics={}
        for phase in ['prefill','decode']:
            line=next(x for x in log.splitlines() if x.startswith(phase+' S3c cpu-gap:'))
            metrics[phase]={k:float(v) for k,v in re.findall(r'(wall|wait|fetch|gap)=([\d.]+)s',line)}
        arms.append({'arm':arm,'metrics':metrics,'disk_read_GiB_observed':max(x['disk_read_bytes'] for x in io)/2**30,'io_samples':len(io),'footprint_peak_GiB':max(x['footprint_bytes'] for x in io)/2**30,'output_sha256':hashlib.sha256((run/arm/'stdout.txt').read_bytes()).hexdigest()})
    assert len({x['output_sha256'] for x in arms})==1
    result={'run':str(run),'raw_hashes_passed':True,'routing_and_batch_reconciliation_passed':True,'route_events':len(routes),'fetch_batches':len(batches),'observed':observed,'selection_seconds':sum(r['selection_seconds'] for r in batches),'read_batch_seconds':sum(r['read_batch_seconds'] for r in batches),'logical_expert_read_GiB':sum(r['logical_bytes'] for r in batches)/2**30,'decode_distinct_layer_experts_per_step':sorted({len(s) for s in step_sets}),'one_decode_step_logical_expert_GiB':len(step_sets[0])*3342336/2**30,'adjacent_decode_step_overlap':{'min':min(overlap),'mean':sum(overlap)/len(overlap),'max':max(overlap),'of':320},'fixed_trace_lfu_simulation':sims,'arms':arms,'limits':['One short coding prompt, not a general agent capability test','Trace-off/on/off uses same instrumented build; sampler overhead common to all arms','OS process-attributed disk counters are sampled, may omit final I/O and include non-expert files; not hardware-only SSD attribution','Larger-cache simulations hold routes fixed and omit memory pressure, changed OS residency and fetch latency; not performance predictions']}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
