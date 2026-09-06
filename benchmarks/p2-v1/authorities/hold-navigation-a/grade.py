import pathlib,sys,json
w=pathlib.Path(sys.argv[1]);assert json.loads((w/'ANSWER.json').read_text())=={'command':'store','handler':'archive.handlers:persist','adapter':'archive.adapters:Journal','table':'archive_entries_v3'}
original=pathlib.Path(__file__).parents[2]/'tasks/hold-navigation-a/input'
for p in original.rglob('*'):
 if p.is_file():assert (w/p.relative_to(original)).read_bytes()==p.read_bytes()
