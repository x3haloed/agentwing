import pathlib,sys,subprocess
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from discount import apply
original=pathlib.Path(__file__).parents[2]/'tasks/hold-recovery-b/input/checks/spec_discount.py';assert (w/'checks/spec_discount.py').read_bytes()==original.read_bytes()
for c,p,e in [(101,50,51),(1,50,1),(999,100,0),(10**18+1,50,500000000000000001)]:assert apply(c,p)==e
for c,p in [(-1,1),(1,101),(1,-1),(True,0),(1,False),(1.5,3)]:
 try:apply(c,p)
 except ValueError:pass
 else:raise AssertionError('invalid value')
r=subprocess.run(['/bin/sh','validate.sh'],cwd=w,capture_output=True,text=True,timeout=10);assert r.returncode==0,r.stderr;assert 'Ran 2 tests' in r.stderr+r.stdout
