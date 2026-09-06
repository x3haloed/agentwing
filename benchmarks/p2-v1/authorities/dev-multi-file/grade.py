import json,pathlib,sys,subprocess,copy
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w))
from ledger.api import list_items
records=[{'id':8,'title':'eight'},{'id':1,'archived':True},{'id':3,'archived':False},{'id':2,'archived':True}]
before=copy.deepcopy(records)
assert list_items(records,1)==[records[2]]
assert list_items(records,2)==[records[2],records[0]]
assert list_items(records,2,include_archived=True)==[records[1],records[3]]
assert list_items([])==[] and records==before
for bad in [0,-1,1.5,True]:
 try:list_items(records,bad)
 except ValueError:pass
 else:raise AssertionError('invalid limit')
(w/'grade-input.json').write_text(json.dumps(records))
for flags,expected in [([], [records[2],records[0]]),(['--include-archived'],[records[1],records[3]])]:
 p=subprocess.run([sys.executable,'-m','ledger.cli','--input','grade-input.json','--limit','2',*flags],cwd=w,capture_output=True,text=True,timeout=10)
 assert p.returncode==0,p.stderr;assert json.loads(p.stdout)==expected
p=subprocess.run([sys.executable,'-m','ledger.cli','--input','grade-input.json','--limit','0'],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode!=0
