import pathlib,sys,json,subprocess,unittest.mock,os
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from catalog.storage import save
area=w/'scratch';area.mkdir();target=area/'output.json';target.write_text('prior')
try:save(target,[{'bad':object()}])
except (TypeError,ValueError):pass
else:raise AssertionError('serialization error missing')
assert target.read_text()=='prior' and len(list(area.iterdir()))==1
with unittest.mock.patch('os.replace',wraps=os.replace) as replace:
 save(str(target),[{'id':2}]);assert replace.call_count==1
assert json.loads(target.read_text())==[{'id':2}]
with unittest.mock.patch('os.replace',side_effect=OSError('injected failure')):
 try:save(target,[{'id':3}])
 except OSError:pass
 else:raise AssertionError('replace error ignored')
assert json.loads(target.read_text())==[{'id':2}] and len(list(area.iterdir()))==1
(w/'input.json').write_text('[{"id":8},{"id":2}]')
for flags,expected in [([],[{'id':8},{'id':2}]),(['--sort-by-id'],[{'id':2},{'id':8}])]:
 p=subprocess.run([sys.executable,'-m','catalog.cli','input.json','result.json',*flags],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr;assert json.loads((w/'result.json').read_text())==expected
(w/'bad.json').write_text('invalid');before=(w/'result.json').read_bytes();p=subprocess.run([sys.executable,'-m','catalog.cli','bad.json','result.json'],cwd=w,capture_output=True,timeout=10);assert p.returncode!=0;assert (w/'result.json').read_bytes()==before
