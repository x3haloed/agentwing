#!/usr/bin/env python3
"""Independently recompute AW199 attention with scalar math.fsum."""
import json,math
from pathlib import Path
import numpy as np
import check_bonsai_attention_oracle as oracle
from run_local_agent import ROOT,digest
R=Path('/Users/chad/Models/agentwing/evidence/AW-0199')
def main():
 result=json.loads((R/'result.json').read_text());assert digest(R/'plan.json')==result['plan_sha256']
 for name,sha in result['raw_sha256'].items():assert digest(R/name)==sha
 oracle.CAPTURE=R.parent/'AW-0109';t=oracle.read_capture();rows=[]
 for row in result['records']:
  layer=row['layer'];v=np.fromfile(R.parent/'AW-0185'/f'{layer}-input.bin',dtype='<f4').reshape(4,48,256)
  assert digest(R.parent/'AW-0185'/f'{layer}-input.bin')==result['input_sha256'][str(layer)]
  weights=[]
  for h in range(24):
   scores=[math.fsum(oracle.value(t[layer,1],d,k,h//6)*oracle.value(t[layer,0],d,0,h) for d in range(256))*.0625 for k in range(48)]
   ex=[math.exp(s-max(scores)) for s in scores];den=math.fsum(ex);weights.append([x/den for x in ex])
  def attention(values):return [math.fsum(weights[h][k]*float(values[h//6,k,d]) for k in range(48)) for h in range(24) for d in range(256)]
  reference=attention(v);norm=math.fsum(x*x for x in reference);errors={}
  for bits in [4,6]:
   out=np.fromfile(R/f'{layer}-{bits}-decoded.bin',dtype='<f4').reshape(v.shape);a=attention(out);e=math.sqrt(math.fsum((x-y)**2 for x,y in zip(a,reference))/norm);assert abs(e-row[str(bits)]['attention_relative_l2'])<1e-12;errors[str(bits)]=e
  assert errors['6']<=.5*errors['4'];rows.append({'layer':layer,'attention_relative_l2':errors})
 audit={'experiment':'AW-0199','passed':True,'result_sha256':digest(R/'result.json'),'auditor_sha256':digest(Path(__file__)),'independent_attention':rows,'base_library_sha256':digest(Path('/Users/chad/Models/agentwing/runtime-builds/prism-turbo-codebook/bin/libggml-base.0.21.0.dylib')),'preserved_failed_attempt_sha256':{p.name:digest(p) for p in (R/'attempt-0-missing-rpath').iterdir()},'limitation':'Independent attention reduction and bit unpacking; inverse WHT shared with native library, no Metal/behavior/endpoint proof'}
 (R/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
