#!/usr/bin/env python3
"""Prepare hash-verified, frozen AW-0141 accumulated-prefix diagnostic inputs."""
import json,hashlib
from pathlib import Path
R=Path('/Users/chad/Models/agentwing/evidence/AW-0144')
S=Path('/Users/chad/Models/agentwing/evidence/AW-0141/20261006T095302.957259Z')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((S/'sha256-recursive.json').read_text());assert all(sha(S/n)==h for n,h in manifest.items())
events=[json.loads(l) for l in (S/'dev-multi-file/pi.jsonl').read_text().splitlines()]
prompts=[]
for line in (S/'dev-multi-file/server.log').read_text().splitlines():
 marker='http: streamed chunk: data: '
 if marker not in line:continue
 try:x=json.loads(line.split(marker,1)[1])
 except json.JSONDecodeError:continue
 if 'generation_settings' in x.get('__verbose',{}):prompts.append(x['__verbose']['prompt'])
assistant=[e['message'] for e in events if e.get('type')=='message_end' and e.get('message',{}).get('role')=='assistant']
ends=[e for e in events if e.get('type')=='tool_execution_end']
def append(prompt,i):
 c=assistant[i]['content'];thought=''.join(z.get('thinking','') for z in c);call=next(z for z in c if z['type']=='toolCall');out=''.join(z.get('text','') for z in ends[i]['result']['content'])
 return prompt+thought+'</think>\n\n<tool_call>\n<function=bash>\n<parameter=command>\n'+call['arguments']['command']+'\n</parameter>\n</function>\n</tool_call><|im_end|>\n<|im_start|>user\n<tool_response>\n'+out.rstrip('\n')+'\n</tool_response><|im_end|>\n<|im_start|>assistant\n<think>\n'
assert append(prompts[0],0)==prompts[1] and append(prompts[1],1)==prompts[2]
base=append(prompts[2],2);deltas=[];turn=0
for e in events:
 if e.get('type')=='message_start' and e.get('message',{}).get('role')=='assistant':turn+=1
 d=e.get('assistantMessageEvent',{})
 if turn==4 and d.get('type')=='thinking_delta':deltas.append(d.get('delta',''))
assert len(deltas)==7695
assert not R.exists();R.mkdir()
files={}
for n in [0,1024,4096,7695]:
 p=R/f'prefix-{n}-chunks.txt';p.write_text(base+''.join(deltas[:n]));files[p.name]={'sha256':sha(p),'bytes':p.stat().st_size,'thinking_chunks':n}
receipt={'experiment':'AW-0144','status':'inputs-prepared-not-executed','source_raw_receipt_sha256':sha(S/'sha256-recursive.json'),'source_evidence':str(S),'external_evidence':str(R),'preparer_sha256':sha(Path(__file__)),'preceding_two_rendered_prefixes_reconstructed_byte_exact':True,'inputs':files,'scope':'Frozen candidate-generated accumulated-prefix inputs, no new inference. Chunk positions are not claimed token positions. Fourth prefix is serializer reconstruction, not directly captured full rendered request; live rendering equivalence remains required before fidelity inference.'}
(R/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
