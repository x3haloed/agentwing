#!/usr/bin/env python3
"""AW207 independent bytes, host trace and predeclared writer cost audit."""
import json,re,statistics
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,digest
R=Path('/Users/chad/Models/agentwing/evidence/AW-0207')
def main():
 plan=json.loads((R/'plan.json').read_text());result=json.loads((R/'result.json').read_text());assert digest(R/'plan.json')==result['plan_sha256'];pairs=[]
 for row in result['rows']:
  i,arm,layer=row['index'],row['arm'],row['layer'];bits=4 if arm=='control' else 6;size=4+16*bits;raw=R/f'{i}-{arm}.bin';assert digest(raw)==row['output_sha256'];assert digest(R/f'{i}-{arm}.log')==row['log_sha256'];a=np.fromfile(raw,dtype=np.uint8).reshape(192,size*2)[::-1].copy().tobytes();assert a==(R.parent/'AW-0199'/f'{layer}-{bits}-packed.bin').read_bytes()
  timing=[float(x) for x in re.findall(r'compute_readback_seconds=([\d.]+)',(R/f'{i}-{arm}.log').read_text())];assert len(timing)==5 and statistics.median(timing[1:])==row['steady_median_seconds']
  trace=np.loadtxt(R/f'{i}-pressure.tsv',ndmin=2);assert len(trace)>0 and max(trace[:,1])<4 and max(trace[:,2])-row['baseline_swap_mib']<=1024;assert row['exit']==0 and not row['error'];capacity=np.loadtxt(R/f'{i}-capacity.tsv',ndmin=2);assert len(capacity)>0 and min(capacity[:,1])>=8*1024**3
 for i in range(0,len(result['rows']),4):
  rows=result['rows'];pairs.extend([rows[i+1]['steady_median_seconds']/rows[i]['steady_median_seconds'],rows[i+2]['steady_median_seconds']/rows[i+3]['steady_median_seconds']])
 assert len(pairs)==6;cost=all(x<=1.35 for x in pairs);assert cost==result['cost_gate_passed'];audit={'experiment':'AW-0207','complete':True,'numeric_and_sampled_host_passed':True,'cost_gate_passed':cost,'paired_ratios':pairs,'result_sha256':digest(R/'result.json'),'auditor_sha256':digest(Path(__file__)),'raw_sha256':{str(p.relative_to(R)):digest(p) for p in R.rglob('*') if p.is_file()},'scope':'Writer screen only; sampled pressure traces verified. Capacity trace independently replayed. Not attention/model/endpoint admission.'};(R/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k!='raw_sha256'},indent=2))
if __name__=='__main__':main()
