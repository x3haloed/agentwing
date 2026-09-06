import pathlib,sys,json,copy,subprocess
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from release.summarize import summarize
expected={'successful_projects':1,'build_ids':['b1']};assert json.loads((w/'totals.json').read_text())==expected
note=(w/'FINDINGS.md').read_text();assert all(x in note for x in ['release/select.py','CONTRACT.md'])
rows=[{'project':'z','build_id':'z10','sequence':10,'status':'failed'},{'project':'z','build_id':'z2','sequence':2,'status':'success'},{'project':'x','build_id':'x3','sequence':3,'status':'success'},{'project':'x','build_id':'x3','sequence':3,'status':'success'}];before=copy.deepcopy(rows);assert summarize(rows)=={'successful_projects':1,'build_ids':['x3']};assert rows==before;assert summarize([])=={'successful_projects':0,'build_ids':[]}
p=subprocess.run([sys.executable,'scripts/export.py','builds.json','cli.json'],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr;assert json.loads((w/'cli.json').read_text())==expected
original=pathlib.Path(__file__).parents[2]/'tasks/hold-investigation-b/input/builds.json';assert (w/'builds.json').read_bytes()==original.read_bytes()
