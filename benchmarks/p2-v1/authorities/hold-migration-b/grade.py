import pathlib,sys,json,subprocess
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from convert import convert
expected={'server':{'port':9090,'enabled':False,'timeout_seconds':2.5,'label':'load 50%'},'extras':{'telemetry':{'endpoint':'/metrics'}}};assert json.loads((w/'migrated.json').read_text())==expected
assert convert('')=={'server':{'port':8080,'enabled':True,'timeout_seconds':1.5},'extras':{}}
for val in ['FALSE','No','0']:assert convert('[server]\nenabled='+val)['server']['enabled'] is False
for key,val in [('port','0'),('port','65536'),('timeout_ms','-1'),('enabled','maybe')]:
 try:convert('[server]\n'+key+'='+val)
 except ValueError:pass
 else:raise AssertionError('invalid setting')
p=subprocess.run([sys.executable,'convert.py','app.ini','cli.json'],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr;assert json.loads((w/'cli.json').read_text())==expected
original=pathlib.Path(__file__).parents[2]/'tasks/hold-migration-b/input/app.ini';assert (w/'app.ini').read_bytes()==original.read_bytes()
