import pathlib,sys,subprocess,json
w=pathlib.Path(sys.argv[1]);expected={'blue':[{'player':'Dee','score':-2,'rank':1}],'red':[{'player':'Ada','score':9,'rank':1},{'player':'Bo','score':9,'rank':1},{'player':'Cy','score':7,'rank':3}]};assert json.loads((w/'ranking.json').read_text())==expected
for text,expected in [('team\tplayer\tscore\n',{}),('team\tplayer\tscore\nt\tz\t5\nt\ta\t5\nt\tb\t3\nt\tb\t2\n',{'t':[{'player':'a','score':5,'rank':1},{'player':'z','score':5,'rank':1},{'player':'b','score':3,'rank':3}]})]:
 text=text.replace('\\t','\t').replace('\\n','\n');(w/'input.tsv').write_text(text)
 p=subprocess.run([sys.executable,'rank.py','input.tsv','out.json'],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr;assert json.loads((w/'out.json').read_text())==expected;assert (w/'input.tsv').read_text()==text

original=pathlib.Path(__file__).parents[2]/'tasks/hold-data-a/input/scores.tsv'
assert (w/'scores.tsv').read_bytes()==original.read_bytes()
