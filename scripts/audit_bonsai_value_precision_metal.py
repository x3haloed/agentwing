#!/usr/bin/env python3
"""AW200 independent file/host/cost replay; exact bytes, no native speed claim."""
import json,re,statistics
from pathlib import Path
from run_local_agent import digest,ROOT
R=Path('/Users/chad/Models/agentwing/evidence/AW-0200');P=R.parent/'AW-0199'
def main():
 result=json.loads((R/'result.json').read_text());plan=json.loads((R/'plan.json').read_text());assert digest(R/'plan.json')==result['plan_sha256'];assert digest(P/'result.json')==plan['parent_result_sha256']
 for name,sha in result['raw_sha256'].items():assert digest(R/name)==sha
 costs={};peak=0;minfree=None;swap=[]
 for row in result['records']:
  d=R/f"{row['layer']}-{row['slot']}-{row['bits']}";bits=row['bits'];layer=row['layer']
  for kind in ['packed','decoded']:assert (d/f'{kind}.bin').read_bytes()==(P/f'{layer}-{bits}-{kind}.bin').read_bytes()
  trace=json.loads((d/'host.json').read_text());assert trace
  for x in trace:
   assert x['pressure']<4 and x['free_bytes']>=8*1024**3;peak=max(peak,x['pressure']);swap.append(x['swap_mib']);minfree=x['free_bytes'] if minfree is None else min(minfree,x['free_bytes'])
  windows=[float(x) for x in re.findall(r'encode_decode_readback_seconds=([0-9.]+)',(d/'log.txt').read_text())];assert len(windows)==5 and all(x>0 for x in windows);costs.setdefault(layer,{}).setdefault(bits,[]).extend(windows)
 assert max(swap)-min(swap)<=1024
 diagnostic=[{'layer':layer,'prototype_median_6_over_4':statistics.median(c[6])/statistics.median(c[4]),'4bit_median_64ops_seconds':statistics.median(c[4]),'6bit_median_64ops_seconds':statistics.median(c[6])} for layer,c in costs.items()]
 audit={'experiment':'AW-0200','passed':True,'result_sha256':digest(R/'result.json'),'auditor_sha256':digest(Path(__file__)),'all_12_packed_and_decoded_byteexact':True,'sampled_peak_pressure':peak,'sampled_swap_range_mib':max(swap)-min(swap),'minimum_free_bytes':minfree,'prototype_cost_diagnostics':diagnostic,'limitations':'Half-second host sampling may miss short peaks. Standalone binary-search4/6 writers and full-block inverse; cost is not native SET_ROWS/flash-attention or endpoint evidence. CPU touches packed output each operation; decoded output independently checked at process end.'}
 (R/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
