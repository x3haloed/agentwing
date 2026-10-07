#!/usr/bin/env python3
"""Independent AW227 component cost audit; no numerical admission waiver."""
import hashlib,json,re
from pathlib import Path
from run_local_agent import ROOT
R=Path('/Users/chad/Models/agentwing/evidence/AW-0227')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 plan=json.loads((R/'plan.json').read_text());summary=json.loads((R/'summary.json').read_text());assert summary['complete'] and summary['error'] is None
 assert sha(ROOT/'scripts/screen_bonsai_checkpoint_cost.py')==plan['runner_sha256']
 for n,h in plan['prerequisites_sha256'].items():assert sha(ROOT/n)==h
 order=['control-1','candidate-1','candidate-2','control-2'];assert [r['arm'] for r in summary['rows']]==order
 rows=[];requests={};tokens=[];commands=[]
 for name in order:
  d=R/name;h=json.loads((d/'hashes.json').read_text());assert h=={p.name:sha(p) for p in d.iterdir() if p.is_file() and p.name!='hashes.json'}
  p=json.loads((d/'plan.json').read_text());result=json.loads((d/'result.json').read_text());assert {'arm':name,**result}==summary['rows'][order.index(name)]
  assert result['error'] is None and result['server_exit']==0 and result['generated_tokens']==640
  commands.append(p['command']);assert p['env']['AGENTWING_GENERATION_CHECKPOINTS']==('1' if name.startswith('candidate') else '0')
  for req in ['tokenize','generate','restored']:requests.setdefault(req,[]).append(sha(d/(req+'-request.json')))
  generated=json.loads((d/'generate-response.json').read_text());restored=json.loads((d/'restored-response.json').read_text());assert generated['stop'] and restored['stop'] and not generated.get('error') and not restored.get('error');tokens.append(generated['tokens']);assert len(tokens[-1])==640 and restored['tokens']==[220]
  s=[json.loads(x) for x in (d/'host.jsonl').read_text().splitlines()];peak=max(x['pressure'] for x in s);growth=max(0,max(x['swap_mib'] for x in s)-s[0]['swap_mib']);free=min(x['free_bytes'] for x in s);assert peak<4 and growth<=1024 and free>=8*1024**3
  log=(d/'server.log').read_bytes().decode('utf-8',errors='surrogateescape');cp=[int(x) for x in re.findall(r'restored context checkpoint .*?n_tokens = (\d+)',log)];assert cp==([531] if name.startswith('candidate') else [16])
  rows.append({'arm':name,'wall_seconds':result['wall_seconds'],'generation_wall':result['generation_wall'],'replay_wall':result['restored_wall'],'restored_checkpoint_tokens':cp,'pressure_peak':peak,'swap_growth_mib':growth,'minimum_free_bytes':free,'raw_receipt_sha256':sha(d/'hashes.json')})
 assert all(c==commands[0] for c in commands) and all(t==tokens[0] for t in tokens)
 assert all(len(set(h))==1 for h in requests.values())
 pair=[{'control':rows[0]['wall_seconds'],'candidate':rows[1]['wall_seconds']},{'control':rows[3]['wall_seconds'],'candidate':rows[2]['wall_seconds']}]
 for p in pair:p['control_over_candidate']=p['control']/p['candidate'];p['cost_gate_passed']=p['candidate']<=p['control']
 assert summary['campaign_wall_seconds']>=sum(r['wall_seconds'] for r in rows)
 return {'experiment':'AW-0227','integrity_audit_passed':True,'component_cost_gate_passed':all(p['cost_gate_passed'] for p in pair),'arms':rows,'pairs':pair,'campaign_wall_seconds':summary['campaign_wall_seconds'],'plan_sha256':sha(R/'plan.json'),'summary_sha256':sha(R/'summary.json'),'identical_requests_and_generated_tokens':True,'raw_location':str(R),'accounting_limit':'Arm wall excludes its final result/hash receipt creation; campaign charges these. Final campaign summary/audit writing excluded. Component diagnostic only, not endpoint promotion accounting.','scope':'Retain cost survivor only; prior AW223numeric gate rejection preserved. No full multimodal/tool/task admission or 25%P1utility claim.'}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
