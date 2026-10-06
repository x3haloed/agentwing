#!/usr/bin/env python3
"""AW166 CPU arithmetic/memory falsifier; no Metal or endpoint speed claim."""
import hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/Users/chad/Models/agentwing/evidence/AW-0170')
SOURCE=Path('/Users/chad/Models/agentwing/runtime-sources/prism-turbo-rollback/ggml/src/ggml-metal/kernels/mul_mv.metal')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reduce8(v):
 while len(v)>1:v=[np.float32(v[i]+v[i+1]) for i in range(0,len(v),2)]
 return v[0]

def evaluate(x):
 codes=(np.arange(256,dtype=np.int32)[:,None]+37*np.arange(26,dtype=np.int32)[None,:])%256
 powers=np.array([3,9,27,81,243],dtype=np.int32)
 g=(np.arange(256)[:,None]*powers[None,:])>>8
 trits=g-3*np.column_stack([np.zeros(256,dtype=np.int32),g[:,:-1]])-1
 # Independent integer-decoded full 128-weight reference.
 weights=np.empty((256,128),dtype=np.int32);tables=[]
 for group in range(24):
  positions=np.arange(5)*(16 if group<16 else 8)+(group if group<16 else 80+group-16)
  weights[:,positions]=trits[codes[:,group]]
  table=np.zeros(256,dtype=np.float32)
  left=np.zeros(27,dtype=np.float32);right=np.zeros(9,dtype=np.float32)
  for j in range(3):left=np.float32(left+np.float32(((np.arange(27)//(3**(2-j)))%3-1)*x[positions[j]]))
  for j in range(2):right=np.float32(right+np.float32(((np.arange(9)//(3**(1-j)))%3-1)*x[positions[j+3]]))
  first=(np.arange(256)*27)>>8;last=((np.arange(256)*243)>>8)-9*first
  decoded=np.column_stack([(first//9)%3,(first//3)%3,first%3,last//3,last%3])-1
  assert np.array_equal(decoded,trits) and first.min()==0 and first.max()==26 and last.min()==0 and last.max()==8
  tables.append(np.float32(left[first]+right[last]))
 control=[];candidate=[];mutated=[]
 for lane in range(8):
  acc=np.zeros(256,dtype=np.float32);new=np.zeros(256,dtype=np.float32);bad=np.zeros(256,dtype=np.float32);sumy=np.float32(0)
  for group in [2*lane,2*lane+1,16+lane]:
   positions=np.arange(5)*(16 if group<16 else 8)+(group if group<16 else 80+group-16)
   y=x[positions];c=np.empty(5,dtype=np.float32);c[:4]=np.float32(y[:4]-np.float32(3*y[1:]));c[4]=y[4]
   for value in y:sumy=np.float32(sumy+value)
   for j in range(5):acc=np.float32(acc+np.float32(g[codes[:,group],j]*c[j]))
   new=np.float32(new+tables[group][codes[:,group]])
   bad=np.float32(bad+tables[group][codes[:,group] ^ (1 if group==0 else 0)])
  q=codes[:,24+(lane&1)];p=3**(lane>>1)
  qtrit=((3*p*q)>>8)-3*((p*q)>>8)
  weights[:,120+lane]=qtrit-1
  acc=np.float32(acc+np.float32(qtrit*x[120+lane]));sumy=np.float32(sumy+x[120+lane])
  control.append(np.float32(acc-sumy));candidate.append(np.float32(new+np.float32((qtrit-1)*x[120+lane])));mutated.append(np.float32(bad+np.float32((qtrit-1)*x[120+lane])))
 a=reduce8(control).astype(np.float64);b=reduce8(candidate).astype(np.float64)
 reference=weights.astype(np.float64)@x.astype(np.float64)
 rel=lambda u,v:float(np.linalg.norm(u-v)/max(np.linalg.norm(v),1e-30))
 return {'candidate_vs_control_relative_L2':rel(b,a),'candidate_vs_integer_reference_relative_L2':rel(b,reference),'control_vs_integer_reference_relative_L2':rel(a,reference),'max_absolute_candidate_control':float(np.max(np.abs(a-b))),'mutation_detected':rel(reduce8(mutated).astype(np.float64),reference)>.0001}

def main():
 OUT.mkdir(exist_ok=True);assert not (OUT/'plan.json').exists()
 inputs=[]
 for prefix in ['0','4096','7695']:
  directory=Path('/Users/chad/Models/agentwing/evidence/AW-0148')/(prefix+'-turbo')
  receipt=json.loads((directory/'result.json').read_text())
  for token in [0,15,31]:
   for layer,index in [(0,1),(31,3),(63,5)]:
    p=directory/f'{token*6+index}-0.bin';assert digest(p)==receipt['raw_sha256'][p.name]
    inputs.append({'prefix_chunks':prefix,'decode_token':token,'layer':layer,'path':str(p),'sha256':digest(p)})
 plan={'experiment':'AW-0170','hypothesis':'Partial 27+9 entry activation LUT preserves PTQ ternary block algebra within CPU relativeL2<=.0001 with plausible single-vector scratch memory.','primary_metric':'Arithmetic/control/reference agreement and table footprint; no throughput claim.','source_sha256':digest(SOURCE),'script_sha256':digest(Path(__file__)),'inputs':inputs,'codes':'256 synthetic packed blocks cover every byte code in every field; 27/9-index decomposition independently matches all five integer trits. Not actual complete weight matrices.','acceptance':'All81 sampled activation blocks finite; relativeL2<=.0001 versus control and integer reference; wrong code index in LUT group0 detected. V1 additive-output mutation preserved but insufficient for indexing coverage.','scope':'CPU float32 emulation only, no Metal FMA/simd fidelity, model inference, output quantization or runtime changes.','python':sys.version,'numpy':np.__version__,'os':subprocess.check_output(['sw_vers'],text=True),'hardware':subprocess.check_output(['sysctl','hw.model','hw.memsize'],text=True),'thermal':subprocess.check_output(['pmset','-g','therm'],text=True),'storage':'Internal SSD; captured inputs; no cold I/O claim.'}
 (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');rows=[]
 for item in inputs:
  v=np.fromfile(item['path'],dtype='<f4');assert v.size==17408 and np.isfinite(v).all()
  for block in [0,v.size//128//2,v.size//128-1]:
   result=evaluate(v[block*128:(block+1)*128]);rows.append({**item,'block':block,**result})
 passed=all(r['candidate_vs_control_relative_L2']<=.0001 and r['candidate_vs_integer_reference_relative_L2']<=.0001 and r['mutation_detected'] for r in rows)
 (OUT/'arithmetic.json').write_text(json.dumps(rows,indent=2)+'\n')
 report={'experiment':'AW-0170','passed':passed,'cases':len(rows),'max_candidate_control_relative_L2':max(r['candidate_vs_control_relative_L2'] for r in rows),'max_candidate_reference_relative_L2':max(r['candidate_vs_integer_reference_relative_L2'] for r in rows),'max_control_reference_relative_L2':max(r['control_vs_integer_reference_relative_L2'] for r in rows),'scratch_bytes_at_17408':17408//128*24*36*4,'weight_bytes_changed':0,'table_f32_values_per_block':864,'old_floor_terms_per_block_per_output_row':136,'remaining_qh_floor_terms_per_block_per_output_row':16,'limitations':'Lookup trades arithmetic for gathered reads and table-build work. Cache hit rate, construction, allocation liveness, real row/scales, GPU numerical fidelity and complete execution cost unknown. Only single-vector candidate; do not allocate per-prefill column.','plan_sha256':digest(OUT/'plan.json'),'arithmetic_sha256':digest(OUT/'arithmetic.json'),'external_evidence':str(OUT)}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if not passed:raise SystemExit(1)

if __name__=='__main__':main()
