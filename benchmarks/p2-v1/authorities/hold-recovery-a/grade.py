import pathlib,sys,subprocess,shutil
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from records import lines
original=pathlib.Path(__file__).parents[2]/'tasks/hold-recovery-a/input/tools/check.py';assert (w/'tools/check.py').read_bytes()==original.read_bytes()
for raw,expected in [(b'\xef\xbb\xbf  a  \r\n\r\n b\n',['  a  ',' b']),(b'\n \t\n',[]),(b'last',['last'])]:
 p=w/'sample';p.write_bytes(raw);assert lines(p)==expected
copy=w.parent/'project with spaces';shutil.copytree(w,copy)
p=subprocess.run(['/bin/sh',str(copy/'tools/verify.sh')],cwd=w.parent,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr;assert 'validated' in p.stdout
