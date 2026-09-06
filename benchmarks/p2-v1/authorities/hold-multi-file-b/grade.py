import pathlib,sys,json,copy,subprocess
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from redactor.api import clean
original=pathlib.Path(__file__).parents[2]/'tasks/hold-multi-file-b/input/redactor/rules.py';assert (w/'redactor/rules.py').read_bytes()==original.read_bytes()
value={'Users':[{'TOKEN':{'nested':1},'name':'雪','meta':[{'password':'s'},0]}],'api_key':None,'safe':[]};before=copy.deepcopy(value)
expected={'Users':[{'TOKEN':'[REDACTED]','name':'雪','meta':[{'password':'[REDACTED]'},0]}],'api_key':'[REDACTED]','safe':[]}
r=clean(value);assert r==expected and value==before;r['safe'].append(1);assert value==before
for scalar in [None,False,3,'text']:assert clean(scalar)==scalar
raw=json.dumps(value)+'\n\n'+json.dumps([{'Token':'x'}])+'\n';raw=raw.replace('\\n','\n');(w/'input.jsonl').write_text(raw)
p=subprocess.run([sys.executable,'-m','redactor.cli','input.jsonl','out.jsonl'],cwd=w,capture_output=True,text=True,timeout=10);assert p.returncode==0,p.stderr
assert [json.loads(x) for x in (w/'out.jsonl').read_text().splitlines()]==[expected,[{'Token':'[REDACTED]'}]];assert (w/'input.jsonl').read_text()==raw
before=(w/'out.jsonl').read_bytes();(w/'bad.jsonl').write_text('{}\ninvalid'.replace('\\n','\n'));p=subprocess.run([sys.executable,'-m','redactor.cli','bad.jsonl','out.jsonl'],cwd=w,capture_output=True,timeout=10);assert p.returncode!=0;assert (w/'out.jsonl').read_bytes()==before
