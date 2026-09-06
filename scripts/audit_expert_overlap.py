import json,hashlib,re
from pathlib import Path
r=Path('/Users/chad/Models/agentwing/evidence/AW-0039/20260906T065000.783222Z');ref=Path('/Users/chad/Models/agentwing/evidence/AW-0037/20260906T063224.469387Z')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for root in (r,ref):
 for f,h in json.loads((root/'sha256.json').read_text()).items():assert digest(root/f)==h,f
fixtures=json.loads((r/'fixtures.json').read_text());assert fixtures==json.loads((ref/'fixtures.json').read_text())
reference=[json.loads(x) for x in (ref/'results.jsonl').read_text().splitlines()]
rows=[json.loads(x) for x in (r/'results.jsonl').read_text().splitlines()];assert len(rows)==360
for i,row in enumerate(rows):
 assert row['arm']==i//72 and row['fixture']==i%72 and row['overlap']==bool((i//72)%2)
 expected=[e['stages_sha256'] for e in reference[i%72]['experts']]
 assert row['stages_sha256']==expected,(i,row['stages_sha256'],expected)
result=json.loads((r/'result.json').read_text());assert result['exit']==0 and result['error'] is None
arms=[dict(arm=int(a),overlap=bool(int(b)),seconds=float(c),process_input_blocks=int(d)) for a,b,c,d in re.findall(r'arm=(\d+) overlap=(\d+) seconds=([\d.]+) inblock=(\d+)',(r/'stderr.txt').read_text())]
assert len(arms)==5
out={'run':str(r),'raw_receipt_sha256':digest(r/'sha256.json'),'reference_receipt_sha256':digest(ref/'sha256.json'),'all_stage_hashes_match_reference':True,'expert_executions':2880,'arms':arms,'candidate_wall_ratios_to_neighbor_control_mean':[arms[i]['seconds']/((arms[i-1]['seconds']+arms[i+1]['seconds'])/2) for i in (1,3)],'pressure_samples':result['pressure_samples'],'swap_baseline_mib':result['swap_baseline_mib'],'disposition':'Retain for full-runtime causal scheduling investigation; not promoted','limits':['All process input-block counters zero; no SSD claim','Three-layer source fixtures only; no accumulated trajectories','No actual LFU cache, shared expert, chunk batching or agent endpoint','Control is one command buffer with per-expert sequencing, not exact P1 all-gate/up then all-down sequence']}
Path('/Users/chad/Repos/agentwing/evidence/AW-0039-overlap-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
