import json,pathlib,sys
w=pathlib.Path(sys.argv[1]);assert json.loads((w/'ANSWER.json').read_text())=={'job':'retention_v2','source_table':'warehouse.event_log','timestamp_column':'occurred_at','excluded_status':'void'}
original=pathlib.Path(__file__).parents[2]/'tasks/hold-navigation-b/input'
for p in original.rglob('*'):
 if p.is_file():assert (w/p.relative_to(original)).read_bytes()==p.read_bytes()
