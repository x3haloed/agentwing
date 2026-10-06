#!/usr/bin/env python3
"""AW165 retrospective within-run iteration windows, never endpoint speed."""
import hashlib,json,re,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=Path('/Users/chad/Models/agentwing/evidence/AW-0162/rollback/server.log')
OUT=Path('/Users/chad/Models/agentwing/evidence/AW-0165')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 terminal=json.loads((ROOT/'evidence/AW-0162-rollback-full-request-terminal.json').read_text())
 result=json.loads((RAW.parent/'result.json').read_text())
 assert digest(RAW)==result['raw_sha256']['server.log']
 starts=[];accepts=[]
 for line in RAW.read_text().splitlines():
  stamp=re.match(r'^(\d+)\.(\d+)\.(\d+)\.(\d+) ',line)
  if not stamp:continue
  t=int(stamp[1])*60+int(stamp[2])+int(stamp[3])/1000+int(stamp[4])/1000000
  m=re.search(r'task 0 \| (?:generate_draft: id=\d+, #tokens=(\d+), #draft=(\d+), pos_next=\d+|slot decode token, id=\d+, n_ctx = 16384, n_tokens = (\d+), truncated = 0)',line)
  if m:starts.append({'t':t,'position':int(m[1] or m[3]),'draft':int(m[2] or 0)})
  m=re.search(r'task 0 \| accepted (\d+)/(\d+) draft tokens, new n_tokens = (\d+)',line)
  if m:accepts.append({'t':t,'accepted':int(m[1]),'draft':int(m[2]),'position':int(m[3])})
 assert len(accepts)==terminal['runtime_verification_counts']['logged_batches']
 windows=[];k=0
 for first,next_ in zip(starts,starts[1:]):
  dt=next_['t']-first['t'];step=next_['position']-first['position']
  assert dt>0 and step>0
  accepted=0
  if first['draft']:
   while k<len(accepts) and accepts[k]['t']<first['t']:k+=1
   assert k<len(accepts) and first['t']<accepts[k]['t']<next_['t']
   row=accepts[k];assert row['draft']==first['draft'] and row['position']==next_['position']
   accepted=row['accepted'];assert step==accepted+1;k+=1
  else:assert step==1
  phase='early' if first['position']<2304 else 'middle' if first['position']<5000 else 'late'
  windows.append({'phase':phase,'kind':'speculative' if first['draft'] else 'single','position':first['position'],'seconds':dt,'output_step':step,'draft':first['draft'],'accepted':accepted})
 groups=[]
 for phase in ['early','middle','late']:
  for kind in ['single','speculative']:
   rows=[x for x in windows if x['phase']==phase and x['kind']==kind]
   assert rows
   seconds=sum(x['seconds'] for x in rows);steps=sum(x['output_step'] for x in rows)
   groups.append({'phase':phase,'kind':kind,'windows':len(rows),'output_steps':steps,'seconds':seconds,'median_iteration_seconds':statistics.median(x['seconds'] for x in rows),'seconds_per_output_step':seconds/steps})
 OUT.mkdir(exist_ok=True)
 (OUT/'windows.json').write_text(json.dumps(windows)+'\n')
 report={'experiment':'AW-0165','status':'retrospective-within-run-diagnostic','source_log_sha256':digest(RAW),'parent_terminal_sha256':digest(ROOT/'evidence/AW-0162-rollback-full-request-terminal.json'),'parent_execution_plan_sha256':digest(RAW.parent.parent/'plan.json'),'script_sha256':digest(Path(__file__)),'groups':groups,'covered_output_steps':sum(x['output_step'] for x in windows),'excluded_final_open_iteration':starts[-1],'raw_windows_sha256':digest(OUT/'windows.json'),'external_evidence':str(OUT),'limitations':'Marker-to-next-marker windows include decode/sampling/streaming/lookup/queue work. Different histories and selection, no matched control, no kernel timing or causal speed ratio. Posthoc phase bins and analysis; full timeout and all cost preserved. Pipeline compilation alone does not establish invocation count.'}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
