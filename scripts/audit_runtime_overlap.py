#!/usr/bin/env python3
"""Audit AW-0040 receipts, complete trajectories, LFU decisions and timings."""
import argparse
import hashlib
import json
from pathlib import Path
import re

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args();run=args.run
    receipt=json.loads((run/'sha256.json').read_text())
    for name,h in receipt.items():assert digest(run/name)==h,name
    summary=json.loads((run/'summary.json').read_text());assert summary['complete']
    manifest=json.loads((run/'manifest.json').read_text())
    cases={};allmatch=True
    for case,_ in manifest['cases']:
        arms=[];trajectories=[];fetches=[];outputs=[]
        for label in ['C1','A1','C2']:
            root=run/(case+'-'+label);result=json.loads((root/'result.json').read_text())
            assert result['exit']==0 and result['error'] is None
            samples=result['pressure_samples'];assert samples and max(x[1] for x in samples)<4 and max(x[2] for x in samples)-result['swap_baseline_mib']<=1024
            rows=[json.loads(x) for x in (root/'routes.jsonl').read_text().splitlines()]
            assert len(rows)<10000 and [r['sequence'] for r in rows]==list(range(len(rows)))
            routes=[(r['layer'],r['experts']) for r in rows if r['event']=='route'];assert routes
            assert all(len(e)==8 and len(set(e))==8 and all(0<=i<256 for i in e) for _,e in routes)
            batches=[(r['layer'],r['experts'],r['misses'],r['logical_bytes']) for r in rows if r['event']=='fetch']
            assert batches and all(b==len(m)*3342336 and set(m)<=set(e) for _,e,m,b in batches)
            trajectories.append(routes);fetches.append(batches);outputs.append(digest(root/'stdout.txt'))
            log=(root/'stderr.txt').read_text();metrics={}
            for phase in ['prefill','decode']:
                line=next(x for x in log.splitlines() if x.startswith(phase+' S3c cpu-gap:'))
                metrics[phase+'_seconds']=float(re.search(r'wall=([\d.]+)s',line)[1])
            io=[json.loads(x) for x in (root/'io.jsonl').read_text().splitlines()];assert len(io)>1
            arms.append(dict(arm=label,wall_seconds=result['wall_seconds'],**metrics,
                sampled_disk_read_gib=max(x['disk_read_bytes'] for x in io)/2**30,
                peak_sampled_footprint_gib=max(x['footprint_bytes'] for x in io)/2**30,
                logical_expert_read_gib=sum(b[3] for b in batches)/2**30,
                route_events=len(routes),fetch_batches=len(batches),max_pressure=max(x[1] for x in samples),
                max_swap_growth_mib=max(x[2] for x in samples)-result['swap_baseline_mib']))
        same=trajectories[0]==trajectories[1]==trajectories[2] and fetches[0]==fetches[1]==fetches[2] and len(set(outputs))==1;allmatch &= same
        ratios={key:arms[1][key]/((arms[0][key]+arms[2][key])/2) for key in ['wall_seconds','prefill_seconds','decode_seconds']}
        cases[case]={'text_routes_and_cache_decisions_match':same,'arms':arms,'candidate_ratios_to_neighbor_control_mean':ratios}
    out={'run':str(run),'raw_receipt_sha256':digest(run/'sha256.json'),'source_revision':manifest['source_revision'],'all_text_routes_and_cache_decisions_match':allmatch,'cases':cases,'limits':['Short development prompts, 12 generated tokens each; no broad capability or utility claim','Sampled process disk bytes include non-expert files and may omit final activity; not hardware-only SSD attribution','Overlap path per-phase fetch and GPU counters are not comparable','Single-token scheduling only; chunked prefill remains unchanged']}
    print(json.dumps(out,indent=2));return 0 if allmatch else 1
if __name__=='__main__':raise SystemExit(main())
