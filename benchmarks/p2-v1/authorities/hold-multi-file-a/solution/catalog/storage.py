import json,os,tempfile
from pathlib import Path
def save(path,records):
 data=json.dumps(records);path=Path(path);temporary=None
 try:
  with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False) as f:
   temporary=f.name;f.write(data)
  os.replace(temporary,path);temporary=None
 finally:
  if temporary is not None:os.unlink(temporary)
