import pathlib,sys,importlib.util,json,copy,subprocess
w=pathlib.Path(sys.argv[1]);s=importlib.util.spec_from_file_location('migration',w/'migrate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
original=pathlib.Path(__file__).parents[2]/'tasks/dev-migration/input/legacy.json';assert (w/'legacy.json').read_bytes()==original.read_bytes()
expected={'schema':2,'network':{'proxy':'http://local','attempts':5,'timeout_ms':7000},'tags':['keep'],'owner':'ops'}
assert json.loads((w/'upgraded.json').read_text())==expected
for inp,out in [({'schema':1},{'schema':2,'network':{'timeout_ms':30000,'attempts':3}}),({'schema':1,'retries':0,'timeout_seconds':0,'network':{'tls':{'on':True}}},{'schema':2,'network':{'tls':{'on':True},'timeout_ms':0,'attempts':1}}),(expected,expected)]:
 before=copy.deepcopy(inp);r=m.upgrade(inp);assert r==out and inp==before and r is not inp
 if 'network' in inp:r['network']['new']=42;assert inp==before
for inp in [{'schema':3},{'schema':True},{'schema':1,'retries':True},{'schema':1,'timeout_seconds':-1},{'schema':1,'retries':2.5}]:
 try:m.upgrade(inp)
 except ValueError:pass
 else:raise AssertionError('invalid accepted')
p=subprocess.run([sys.executable,'migrate.py','legacy.json','cli.json'],cwd=w,text=True,capture_output=True,timeout=10);assert p.returncode==0,p.stderr;assert json.loads((w/'cli.json').read_text())==expected
