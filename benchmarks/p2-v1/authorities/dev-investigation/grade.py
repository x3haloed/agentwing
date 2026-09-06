import pathlib,sys,json,copy,subprocess
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w))
from jobs.join import enrich
from jobs.export import export
expected={'north':1000,'south':700};assert json.loads((w/'revenue.json').read_text())==expected
f=json.loads((w/'FINDINGS.json').read_text());assert isinstance(f['cause'],str) and len(f['cause'])>20;assert f['corrected_totals']==expected
assert 'jobs/join.py' in f['evidence'] and len(set(f['evidence']))>=2
assert all((w/p).is_file() for p in f['evidence'])
original=pathlib.Path(__file__).parents[2]/'tasks/dev-investigation/input/data'
for p in original.iterdir():assert (w/'data'/p.name).read_bytes()==p.read_bytes()
customers=[{'tenant_id':t,'customer_id':9,'name':t.upper()} for t in ['z','a','b']]
invoices=[{'tenant_id':'a','customer_id':9,'cents':13},{'tenant_id':'z','customer_id':9,'cents':-4},{'tenant_id':'a','customer_id':9,'cents':2}]
before=copy.deepcopy([customers,invoices]);assert export(invoices,customers)=={'a':15,'z':-4}
r=enrich(invoices,customers);assert len(r)==3 and [x['name'] for x in r]==['A','Z','A'];assert [customers,invoices]==before
try:enrich([{'tenant_id':'missing','customer_id':9,'cents':1}],customers)
except ValueError:pass
else:raise AssertionError('unknown customer dropped')
p=subprocess.run([sys.executable,'-m','jobs.export','data/invoices.json','data/customers.json','cli.json'],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr;assert json.loads((w/'cli.json').read_text())==expected
