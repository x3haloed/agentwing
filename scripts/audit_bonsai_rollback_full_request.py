#!/usr/bin/env python3
"""Independent AW-0162 full-request stream/hash audit; proposals never execute."""
import argparse,json,math
from pathlib import Path
from run_local_agent import ROOT,digest
R=Path('/Users/chad/Models/agentwing/evidence/AW-0162')

def strict_json(data):
 def constant(value):raise ValueError('Non-JSON constant: '+value)
 def pairs(values):
  result={}
  for key,value in values:
   if key in result:raise ValueError('Duplicate JSON key: '+key)
   result[key]=value
  return result
 return json.loads(data,parse_constant=constant,object_pairs_hook=pairs)

def stream(path):
 events=0;ids=set();finish=[];done=False;done_count=0;thinking=0;text=0;tools={};errors=[]
 for line in path.read_bytes().splitlines():
  if not line.startswith(b'data: '):continue
  data=line[6:].strip()
  if data==b'[DONE]':done=True;done_count+=1;continue
  if done:errors.append('data-after-DONE')
  try:x=strict_json(data)
  except ValueError as exc:errors.append(str(exc));continue
  events+=1
  if x.get('id'):ids.add(x['id'])
  if x.get('error'):errors.append(x['error'])
  for choice in x.get('choices',[]):
   if choice.get('index',0)!=0:errors.append('unexpected-choice-index')
   if choice.get('finish_reason') is not None:finish.append(choice['finish_reason'])
   delta=choice.get('delta',{});thinking+=len(delta.get('reasoning_content','') or '');text+=len(delta.get('content','') or '')
   for call in delta.get('tool_calls',[]):
    item=tools.setdefault(call['index'],{'id':'','name':'','arguments':''})
    if call.get('type','function')!='function':errors.append('unexpected-tool-type')
    if call.get('id'):
     if item['id'] and item['id']!=call['id']:errors.append('tool-id-changed')
     item['id']=call['id']
    fn=call.get('function',{});item['name']+=fn.get('name','');item['arguments']+=fn.get('arguments','')
 proposals=[]
 for index,item in sorted(tools.items()):
  parsed=None;valid=False
  try:
   parsed=strict_json(item['arguments']);valid=item['name']=='bash' and isinstance(parsed,dict) and set(parsed)<={'command','timeout'} and isinstance(parsed.get('command'),str) and bool(parsed['command'].strip()) and ('timeout' not in parsed or isinstance(parsed['timeout'],(int,float)) and not isinstance(parsed['timeout'],bool) and math.isfinite(parsed['timeout']))
  except (ValueError,TypeError):pass
  proposals.append({'index':index,'id':item['id'],'name':item['name'],'valid_schema':valid,'arguments':parsed,'classification':'valid-proposal' if valid else 'malformed-proposal' if done else 'incomplete-proposal','raw_arguments_sha256':__import__('hashlib').sha256(item['arguments'].encode()).hexdigest(),'executed':False,'productive':None})
 return {'events':events,'completion_ids':sorted(ids),'finish_reasons':finish,'done':done,'done_count':done_count,'thinking_characters':thinking,'answer_characters':text,'errors':errors,'proposals':proposals,'terminal_protocol_passed':done_count==1 and len(ids)==1 and len(finish)==1 and not errors and all(t['valid_schema'] and t['id'] for t in proposals) and len({t['id'] for t in proposals})==len(proposals) and finish[0] in ['stop','length','tool_calls'] and (finish[0]!='tool_calls' or bool(proposals)),'tools_executed':0}

def audit(partial=False):
 plan=json.loads((R/'plan.json').read_text());assert digest(ROOT/'scripts/replay_bonsai_rollback_full_request.py')==plan['harness_sha256'];assert digest(ROOT/'spec/bonsai-turbo-rollback-local.json')==plan['runtime_spec_sha256']
 rows=[];request_hashes=set()
 for arm in plan['order']:
  d=R/arm
  if not (d/'result.json').exists():
   if partial:continue
   raise AssertionError('Arm not terminal')
  row=json.loads((d/'result.json').read_text());actual={p.name:digest(p) for p in d.iterdir() if p.is_file() and p.name!='result.json'};assert actual==row['raw_sha256']
  assert json.loads((d/'request.json').read_text())==plan['request'];request_hashes.add(digest(d/'request.json'))
  cmd=json.loads((d/'server-command.json').read_text());assert cmd[cmd.index('--ctx-size')+1]=='16384';assert cmd[cmd.index('--parallel')+1]=='1';assert '--no-context-shift' in cmd;assert cmd[cmd.index('--reasoning-effort')+1]=='medium'
  native=(d/'server.log').read_text();allocation=next(l for l in native.splitlines() if 'K (' in l and 'V (' in l);assert ('K (f16):' in allocation and 'V (f16):' in allocation) if arm=='f16' else ('K (q8_0):' in allocation and 'V (turbo4):' in allocation)
  assert 'n_rs_seq              = 3' in native;assert 'speculative decoding enabled: ngram-simple' in native;assert cmd[cmd.index('--spec-ngram-simple-size-n')+1]=='2' and cmd[cmd.index('--spec-ngram-simple-size-m')+1]=='3'
  response=stream(d/'response.sse');host=row['pressure_peak']<4 and row['swap_growth_peak_mib']<=1024
  rows.append({'arm':arm,'result_sha256':digest(d/'result.json'),'error':row['error'],'client_exit':row['client_exit'],'server_exit_after_cleanup':row['server_exit_after_cleanup'],'host_passed':host,'response':response,'wall_seconds_diagnostic':row['wall_seconds_diagnostic']})
 assert len(request_hashes)<=1
 complete=len(rows)==1
 if complete:assert json.loads((R/'summary.json').read_text())['rows']==[json.loads((R/arm/'result.json').read_text()) for arm in plan['order']]
 return {'experiment':'AW-0162','complete':complete,'rows':rows,'plan_sha256':digest(R/'plan.json'),'auditor_sha256':digest(Path(__file__)),'scope':'One full native request with bounded rollback; no proposal execution, task score, performance ratio or causal qualification'}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--partial',action='store_true');args=parser.parse_args();print(json.dumps(audit(args.partial),indent=2))
