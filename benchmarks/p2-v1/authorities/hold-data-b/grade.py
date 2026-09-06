import pathlib,sys,json,copy,subprocess
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from durations import totals
assert json.loads((w/'totals.json').read_text())=={'api':7200}
rows=[{'session':'a','kind':'start','at':'2026-01-01T12:00:00+02:00','service':'z'},{'session':'a','kind':'stop','at':'2026-01-01T10:01:00Z','service':'z'},{'session':'a','kind':'start','at':'2026-01-01T09:59:00Z','service':'a'},{'session':'a','kind':'stop','at':'2026-01-01T10:02:00Z','service':'z'}];before=copy.deepcopy(rows);assert totals(rows)=={'a':180} and rows==before;assert totals([])=={}
assert totals([rows[0]])=={}
bad=[dict(rows[0],at='2026-01-01T12:00:00Z'),rows[1]]
try:totals(bad)
except ValueError:pass
else:raise AssertionError('negative duration')
p=subprocess.run([sys.executable,'durations.py','events.json','cli.json'],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr;assert json.loads((w/'cli.json').read_text())=={'api':7200}
original=pathlib.Path(__file__).parents[2]/'tasks/hold-data-b/input/events.json';assert (w/'events.json').read_bytes()==original.read_bytes()
