import json, pathlib, sys
w=pathlib.Path(sys.argv[1]);r=json.loads((w/'ANSWER.json').read_text())
assert r['retry_ms']==1250 and type(r['retry_ms']) is int
assert r['attempts']==8 and r['profile']=='edge'
assert set(r['evidence'])=={'deploy/active.env','deploy/launch.sh','relay/config.py'}
# The task promises no changes to repository inputs.
original=pathlib.Path(__file__).parents[2]/'tasks/dev-navigation/input'
for p in original.rglob('*'):
 if p.is_file():assert (w/p.relative_to(original)).read_bytes()==p.read_bytes(),str(p)
