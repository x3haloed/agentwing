#!/usr/bin/env python3
"""AW-0107 independent masked attention oracle from complete actual captures."""
import hashlib,json,math,struct,subprocess
from pathlib import Path
from run_local_agent import preflight,host_sample,check_sample
CAPTURE=Path('/Users/chad/Models/agentwing/evidence/AW-0106');R=Path('/Users/chad/Models/agentwing/evidence/AW-0107')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_capture():
 result=json.loads((CAPTURE/'result.json').read_text());assert result['passed'];tensors={}
 for line in (CAPTURE/'capture.tsv').read_text().splitlines():
  f=line.split('\t');layer,role,kind,size=map(int,f[:4]);ne=list(map(int,f[4:8]));nb=list(map(int,f[8:12]));scale=float(f[12]);p=CAPTURE/f'{layer}-{role}.bin';assert digest(p)==result['capture_files'][p.name]['sha256'];data=p.read_bytes();assert len(data)==size
  tensors[layer,role]={'type':kind,'ne':ne,'nb':nb,'scale':scale,'data':data}
 return tensors
def value(t,d=0,token=0,head=0):
 offset=d*t['nb'][0]+token*t['nb'][1]+head*t['nb'][2];return struct.unpack_from('<f' if t['type']==0 else '<e',t['data'],offset)[0]
def main():
 preflight();baseline=host_sample();R.mkdir(exist_ok=True)
 plan={'experiment':'AW-0107','capture_result_sha256':digest(CAPTURE/'result.json'),'capture_index_sha256':digest(CAPTURE/'capture.tsv'),'script_sha256':digest(Path(__file__)),'layers':[3,31,63],'acceptance':'Each complete output relative L2<=1e-3, finite active Q/K/V/output; rotated KV-head negative must fail','relative_l2_limit':1e-3,'scope':'Independent double dot/softmax/value CPU oracle against native FP16-KV flash attention, one raw16-token prompt; no cache quantization/endpoint acceptance'}
 assert not (R/'plan.json').exists();(R/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');tensors=read_capture();records=[];error=None
 try:
  for layer in plan['layers']:
   q,k,v,mask,out=[tensors[layer,i] for i in range(5)];assert q['ne']==[256,16,24,1] and k['ne']==v['ne']==[256,256,4,1] and out['ne']==[256,24,16,1]
   queries=[[[value(q,d,t,h) for d in range(256)] for t in range(16)] for h in range(24)]
   keys=[[[value(k,d,t,h) for d in range(256)] for t in range(16)] for h in range(4)];vals=[[[value(v,d,t,h) for d in range(256)] for t in range(16)] for h in range(4)]
   assert all(math.isfinite(x) for vectors in [queries,keys,vals] for h in vectors for row in h for x in row)
   expected=[];native=[];negative=[]
   for h in range(24):
    for token in range(16):
     active=[i for i in range(256) if math.isfinite(value(mask,i,token))];assert active==list(range(token+1))
     def compute(kh):
      scores=[q['scale']*math.fsum(a*b for a,b in zip(queries[h][token],keys[kh][i]))+value(mask,i,token) for i in active];maximum=max(scores);w=[math.exp(s-maximum) for s in scores];norm=math.fsum(w);w=[x/norm for x in w];return [math.fsum(weight*vals[kh][i][d] for i,weight in zip(active,w)) for d in range(256)]
     expected.extend(compute(h//6));negative.extend(compute((h//6+1)%4));native.extend(value(out,d,h,token) for d in range(256))
   assert all(math.isfinite(x) for x in native);norm=math.fsum(x*x for x in expected);relative=math.sqrt(math.fsum((x-y)**2 for x,y in zip(native,expected))/norm);wrong=math.sqrt(math.fsum((x-y)**2 for x,y in zip(native,negative))/norm)
   assert relative<=1e-3 and wrong>1e-3;records.append({'layer':layer,'native_vs_cpu_relative_l2':relative,'rotated_kv_head_relative_l2':wrong,'output_values':len(native),'active_key_positions_per_query':[i+1 for i in range(16)],'gqa_query_heads_per_kv_head':6})
 except Exception as exc:error=str(exc) or type(exc).__name__
 after=host_sample();check_sample(after,baseline[1]);result={'experiment':'AW-0107','passed':len(records)==3 and error is None,'error':error,'records':records,'plan_sha256':digest(R/'plan.json'),'phase_host_samples':[baseline,after],'os':subprocess.check_output(['sw_vers'],text=True),'external_evidence':str(R),'scope':plan['scope']};(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
