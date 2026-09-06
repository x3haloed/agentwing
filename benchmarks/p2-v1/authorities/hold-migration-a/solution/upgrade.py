import copy,json,sys
def upgrade(config):
 out=copy.deepcopy(config)
 if type(out.get('version')) is not int or out['version'] not in (1,2):raise ValueError('version')
 if out['version']==2:return out
 flags={}
 for r in out.get('flags',[]):
  name=r.get('name')
  if not isinstance(name,str) or not name or name in flags or type(r.get('enabled')) is not bool:raise ValueError('flag')
  flags[name]={k:v for k,v in r.items() if k!='name'}
 out['flags']=flags;out['version']=2;return out
if __name__=='__main__':
 with open(sys.argv[1]) as f:c=json.load(f)
 with open(sys.argv[2],'w') as f:json.dump(upgrade(c),f)
