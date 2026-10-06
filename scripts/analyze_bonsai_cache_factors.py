#!/usr/bin/env python3
"""Supplement AW181 identical-prefix logits; never changes its acceptance gate."""
import json
from pathlib import Path
import numpy as np
from audit_bonsai_native_mixed_cache_replay import audit,R
from run_local_agent import digest

def distribution(logits):
 # Native order: top_k(20), top_p(.95), min_p(.05), temperature(1).
 ids=np.argsort(-logits,kind='stable')[:20];z=logits[ids];p=np.exp(z-z.max());p/=p.sum()
 keep=np.searchsorted(np.cumsum(p),.95,side='left')+1;ids=ids[:keep];p=p[:keep];p/=p.sum()
 keep=p>=.05*p.max();ids=ids[keep];p=p[keep];p/=p.sum()
 result=np.zeros(logits.size);result[ids]=p;return result

def main():
 checked=audit();assert checked['passed'], 'All four original numeric/resource gates must pass first'
 arms=['f16','q8-f16','f16-turbo','turbo'];rows={}
 for arm in arms:
  d=R/f'7695-{arm}';x=np.fromfile(d/'logits.bin',dtype='<f4').reshape(32,248320)[0].astype(float);assert np.isfinite(x).all();rows[arm]=x
  log=(d/'native.log').read_text()
  if arm in ['q8-f16','f16-turbo']:
   typ='kq8_0_vf16' if arm=='q8-f16' else 'kf16_vturbo4'
   assert 'loaded kernel_flash_attn_ext_'+typ+'_dk256_dv256' in log
   assert 'loaded kernel_flash_attn_ext_vec_'+typ+'_dk256_dv256' in log
 baseline=rows['f16'];deltas={k:v-baseline for k,v in rows.items() if k!='f16'};interaction=deltas['turbo']-deltas['q8-f16']-deltas['f16-turbo'];p=distribution(baseline);out=[]
 for arm in arms[1:]:
  q=distribution(rows[arm]);m=(p+q)/2;js=0.
  for z in [p,q]:
   active=z>0;js+=.5*float(np.sum(z[active]*np.log(z[active]/m[active])))
  delta=deltas[arm]
  out.append({'arm':arm,'delta_l2':float(np.linalg.norm(delta)),'centered_delta_l2':float(np.linalg.norm(delta-delta.mean())),'top1_equal':int(np.argmax(baseline))==int(np.argmax(rows[arm])),'sampling_total_variation':float(np.abs(p-q).sum()/2),'sampling_js_nats':js,'sampled_support_count':int((q>0).sum()),'logits_sha256':digest(R/f'7695-{arm}/logits.bin')})
 result={'experiment':'AW-0181','complete':True,'original_gates_unchanged':checked,'effects':out,'interaction_l2':float(np.linalg.norm(interaction)),'interaction_centered_l2':float(np.linalg.norm(interaction-interaction.mean())),'analysis_source_sha256':digest(Path(__file__)),'scope':'Supplementary same-input first-logit displacement and native-profile probability diagnostic. Float64 probability reference does not prove bitexact native sampler. Nonlinearity retained, not additive causal decomposition or endpoint quality/performance.'}
 print(json.dumps(result,indent=2))

if __name__=='__main__':main()
