#!/usr/bin/env python3
"""Replay AW204 native/CPU payload comparisons and captured boundary values."""
import json
from pathlib import Path
import numpy as np
from run_local_agent import ROOT,digest
from probe_bonsai_turbo6_math_mode import codes,R,P
def main():
 result=json.loads((R/'result.json').read_text());plan=json.loads((R/'plan.json').read_text());assert digest(R/'plan.json')==result['plan_sha256']
 for name,sha in result['raw_sha256'].items():assert digest(R/name)==sha
 native=np.fromfile(R.parent/'AW-0203/attempt-1/1-candidate.bin',dtype=np.uint8).reshape(192,200)[::-1].copy().tobytes();rows=[];samples=[]
 for row in result['records']:
  bits,fast=row['bits'],row['fast_math'];d=R/f'{bits}-{fast}';raw=(d/'packed.bin').read_bytes();cpu=(P/f'3-{bits}-packed.bin').read_bytes();assert int(np.count_nonzero(codes(raw,bits)!=codes(cpu,bits)))==row['cpu_mismatched_codes'];assert (raw==cpu)==row['cpu_packed_byteexact'];samples.extend(json.loads((d/'host.json').read_text()))
  if bits==6:assert (raw==native)==row['native_packed_byteexact']
  rows.append(row)
 assert next(x for x in rows if x['bits']==6 and x['fast_math']==1)['native_packed_byteexact'];assert next(x for x in rows if x['bits']==6 and x['fast_math']==0)['cpu_packed_byteexact'];assert all(x['pressure']<4 and x['free_bytes']>=8*1024**3 for x in samples);swap=[x['swap_mib'] for x in samples];assert max(swap)-min(swap)<=1024
 audit={'experiment':'AW-0204','passed':True,'result_sha256':digest(R/'result.json'),'auditor_sha256':digest(Path(__file__)),'fast_mode_reproduces_entire_native_packed_fixture':True,'precise_mode_reproduces_entire_cpu_packed_fixture':True,'sampled_pressure_peak':max(x['pressure'] for x in samples),'sampled_swap_range_mib':max(swap)-min(swap),'scope':'Standalone mode intervention reproduces native fixture, not direct capture from native SET_ROWS. No writer admission or cost/agent inference.'};(R/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
