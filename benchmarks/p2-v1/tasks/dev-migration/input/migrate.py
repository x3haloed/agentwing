import json,sys
def upgrade(config):
 config['schema']=2
 config['network']={'timeout_ms':config.pop('timeout_seconds',30)*1000,'attempts':config.pop('retries',2)}
 return config
if __name__=='__main__':
 with open(sys.argv[1]) as f:c=json.load(f)
 with open(sys.argv[2],'w') as f:json.dump(upgrade(c),f)
