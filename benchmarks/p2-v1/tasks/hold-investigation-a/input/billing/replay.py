import json,sys
from .project import project
if __name__=='__main__':
 with open(sys.argv[1]) as f:events=json.load(f)
 with open(sys.argv[2],'w') as f:json.dump(project(events),f)
