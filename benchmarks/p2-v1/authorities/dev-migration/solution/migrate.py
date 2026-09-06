import copy,json,sys
def upgrade(config):
 result=copy.deepcopy(config)
 if type(result.get('schema')) is not int or result['schema'] not in (1,2):raise ValueError('schema')
 if result['schema']==2:return result
 timeout=result.get('timeout_seconds',30);retries=result.get('retries',2)
 if any(type(x) is not int or x<0 for x in (timeout,retries)):raise ValueError('invalid setting')
 network=result.setdefault('network',{})
 network.update(timeout_ms=timeout*1000,attempts=retries+1)
 result.pop('timeout_seconds',None);result.pop('retries',None);result['schema']=2
 return result
if __name__=='__main__':
 with open(sys.argv[1]) as f:c=json.load(f)
 with open(sys.argv[2],'w') as f:json.dump(upgrade(c),f)
