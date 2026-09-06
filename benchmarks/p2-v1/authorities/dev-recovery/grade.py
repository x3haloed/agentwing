import pathlib,sys,subprocess,importlib.util
w=pathlib.Path(sys.argv[1]);original=pathlib.Path(__file__).parents[2]/'tasks/dev-recovery/input'
assert (w/'tools/check.py').read_bytes()==(original/'tools/check.py').read_bytes()
s=importlib.util.spec_from_file_location('queue_names',w/'queue_names.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for a,b in [(' High--Priority ','high_priority'),('Straße','strasse'),('A\t\n B','a_b'),('foo__bar','foo__bar'),(' -- 	 ',''),('ALREADY_ok','already_ok'),('équipe--nord','équipe_nord')]:assert m.normalize(a)==b,(a,b)
p=subprocess.run([sys.executable,'tools/check.py'],cwd=w,text=True,capture_output=True,timeout=10);assert p.returncode==0,p.stderr
assert 'python3 tools/check.py' in (w/'VALIDATION.md').read_text()
