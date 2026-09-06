import json,sys
from datetime import datetime
def totals(events):
 groups={}
 for e in events:
  t=datetime.fromisoformat(e['at'].replace('Z','+00:00'));g=groups.setdefault(e['session'],{})
  if e['kind']=='start' and ('start' not in g or t<g['start'][0]):g['start']=(t,e['service'])
  if e['kind']=='stop' and ('stop' not in g or t>g['stop']):g['stop']=t
 out={}
 for g in groups.values():
  if 'start' not in g or 'stop' not in g:continue
  seconds=int((g['stop']-g['start'][0]).total_seconds())
  if seconds<0:raise ValueError('negative duration')
  service=g['start'][1];out[service]=out.get(service,0)+seconds
 return dict(sorted(out.items()))
if __name__=='__main__':
 with open(sys.argv[1]) as f:events=json.load(f)
 with open(sys.argv[2],'w') as f:json.dump(totals(events),f)
