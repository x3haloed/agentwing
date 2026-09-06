def latest(builds):
 out={}
 for b in builds:
  if b['project'] not in out or b['sequence']>out[b['project']]['sequence']:out[b['project']]=b
 return out
