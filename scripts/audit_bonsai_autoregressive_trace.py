#!/usr/bin/env python3
"""Independent AW-0098 complete finiteness/shape/hash audit."""
import hashlib,json,math,struct
from pathlib import Path
R=Path('/Users/chad/Models/agentwing/evidence/AW-0098');result=json.loads((R/'result.json').read_text());runs=json.loads((R/'run-hashes.json').read_text());plan=json.loads((R/'plan.json').read_text())
assert result['passed'];audits=[]
for run in runs:
 case=Path(run['directory']);capture=[];tokens=[]
 for line in (case/'capture.tsv').read_text().splitlines():
  parts=line.split('\t')
  if parts[0]=='TOKEN':tokens.append(int(parts[2]));nv=int(parts[3])
  else:
   assert len(parts)==7;index,side=int(parts[0]),int(parts[1]);width,columns,size=map(int,parts[4:]);path=case/f'{index}-{side}.bin';assert path.stat().st_size==size==width*columns*4;capture.append((index,side,parts[2],columns))
 assert tokens==run['tokens'] and len(tokens)==32 and len(capture)==396
 assert sorted((x[0],x[1]) for x in capture)==[(i,k) for i in range(198) for k in range(2)]
 assert all(x[3]==16 for x in capture if x[0]<6) and all(x[3]==1 for x in capture if x[0]>=6)
 assert (case/'logits.bin').stat().st_size==len(tokens)*nv*4
 floats=0
 for name,expected in run['files'].items():
  path=case/name;assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
  if path.suffix=='.bin':
   data=path.read_bytes();assert all(math.isfinite(v[0]) for v in struct.iter_unpack('<f',data));floats+=len(data)//4
 audits.append({'arm':run['arm'],'selected_nodes':198,'complete_tensor_files':396,'generated_tokens':32,'all_finite_f32_values':floats,'hashes_verified':len(run['files'])})
receipt={'experiment':'AW-0098','passed':True,'audits':audits,'plan_sha256':hashlib.sha256((R/'plan.json').read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'raw_result_sha256':hashlib.sha256((R/'result.json').read_bytes()).hexdigest(),'scope':'Complete raw trace hashes, finite values and shape coverage on bounded raw prompt; no task verifier'}
(R/'independent-trace-audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
