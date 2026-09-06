import pathlib,sys,subprocess,json
w=pathlib.Path(sys.argv[1]);assert json.loads((w/'report.json').read_text())=={'events':2,'cents_by_service':{'api,west':125,'worker':-25}}
cases=[('''event_id,revision,service,cents,deleted
''',{'events':0,'cents_by_service':{}}),('''event_id,revision,service,cents,deleted
x,10,z,9,0
x,2,z,500,0
y,1,a,-10,0
x,10,z,9,0
''',{'events':2,'cents_by_service':{'a':-10,'z':9}}),('''event_id,revision,service,cents,deleted
a,1,a,5,0
a,3,a,5,1
a,2,a,15,0
b,1,b,7,1
b,2,b,8,0
''',{'events':1,'cents_by_service':{'b':8}})]
for raw,expected in cases:
 (w/'case.csv').write_text(raw);(w/'out.json').write_text('old content')
 p=subprocess.run([sys.executable,'summarize.py','case.csv','out.json'],cwd=w,text=True,capture_output=True,timeout=10);assert p.returncode==0,p.stderr
 result=json.loads((w/'out.json').read_text());assert result==expected;assert list(result['cents_by_service'])==sorted(result['cents_by_service']);assert (w/'case.csv').read_text()==raw

original=pathlib.Path(__file__).parents[2]/'tasks/dev-data/input/events.csv'
assert (w/'events.csv').read_bytes()==original.read_bytes()
