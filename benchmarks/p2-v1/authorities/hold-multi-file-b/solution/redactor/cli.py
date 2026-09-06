import json,sys
from .api import clean
if __name__=='__main__':
 with open(sys.argv[1]) as f:rows=[clean(json.loads(line)) for line in f if line.strip()]
 with open(sys.argv[2],'w') as f:
  for row in rows:f.write(json.dumps(row,ensure_ascii=False)+chr(10))
