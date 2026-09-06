import pathlib,sys,json,copy,subprocess
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from upgrade import upgrade
expected={'version':2,'owner':'eng','flags':{'search':{'enabled':True,'rollout':{'pct':50}},'export':{'enabled':False}}};assert json.loads((w/'result.json').read_text())==expected
source=json.loads((w/'flags.json').read_text());before=copy.deepcopy(source);out=upgrade(source);assert out==expected and source==before;out['flags']['search']['rollout']['pct']=0;assert source==before
assert upgrade({'version':1})=={'version':2,'flags':{}}
out=upgrade(expected);out['flags']['search']['rollout']['pct']=0;assert expected['flags']['search']['rollout']['pct']==50
for bad in [{'version':3},{'version':True},{'version':1,'flags':[{'name':'x','enabled':1}]},{'version':1,'flags':[{'name':'','enabled':False}]},{'version':1,'flags':[{'name':'x','enabled':True},{'name':'x','enabled':False}]}]:
 try:upgrade(bad)
 except ValueError:pass
 else:raise AssertionError('invalid migration accepted')
p=subprocess.run([sys.executable,'upgrade.py','flags.json','cli.json'],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr;assert json.loads((w/'cli.json').read_text())==expected;assert json.loads((w/'flags.json').read_text())==before

original=pathlib.Path(__file__).parents[2]/'tasks/hold-migration-a/input/flags.json'
assert (w/'flags.json').read_bytes()==original.read_bytes()
