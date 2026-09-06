import json,sys
from .api import clean
if __name__=='__main__':
 with open(sys.argv[1]) as f:value=json.load(f)
 with open(sys.argv[2],'w') as f:json.dump(clean(value),f)
