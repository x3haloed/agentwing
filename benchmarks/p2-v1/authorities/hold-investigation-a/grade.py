import pathlib,sys,json,copy,subprocess
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from billing.project import project
expected={'a/cash':0,'b/cash':50};assert json.loads((w/'balances.json').read_text())==expected
note=(w/'FINDINGS.md').read_text();assert 'billing/project.py' in note and 'docs/runbook.md' in note
rows=[{'tenant':'x','account':'one','event_id':'k','delta':7},{'tenant':'x','account':'two','event_id':'k','delta':900},{'tenant':'y','account':'one','event_id':'k','delta':2}];before=copy.deepcopy(rows);assert project(rows)=={'x/one':7,'y/one':2};assert rows==before;assert project([])=={}
p=subprocess.run([sys.executable,'-m','billing.replay','events.json','cli.json'],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr;assert json.loads((w/'cli.json').read_text())==expected
original=pathlib.Path(__file__).parents[2]/'tasks/hold-investigation-a/input/events.json';assert (w/'events.json').read_bytes()==original.read_bytes()
