#!/usr/bin/env python3
"""AW-0101 static contract compatibility check; changes no policy."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
paths=['spec/p2-acceptance.json','spec/validated-local-agent.json','spec/bonsai-selective-local.json']
policy,control,candidate=[json.loads((ROOT/p).read_text()) for p in paths]
a=control['settings'];b=dict(candidate['sampling'])
import bonsai_selective_server
command=bonsai_selective_server.command();b['frequency_penalty']=float(command[command.index('--frequency-penalty')+1])
paths+=['scripts/bonsai_selective_server.py','scripts/bonsai_server.py']
differences={key:{'control':a.get(key),'candidate':b.get(key)} for key in ['temperature','top_p','top_k','presence_penalty','frequency_penalty'] if a.get(key)!=(b.get(key,0) if key=='frequency_penalty' else b.get(key))}
differences['output_budget']={'control':a['max_output_tokens'],'candidate':candidate['max_output_tokens']}
differences['reasoning']={'control_enable_thinking':a['enable_thinking'],'candidate_effort':candidate['reasoning_effort']}
matched=policy['invariants']['matched_prompt_sampling_context_tool_permissions_and_timeout_between_arms'];result={'experiment':'AW-0101','existing_contract_compatible':not matched or not differences,'matched_configuration_invariant':matched,'differences':differences,'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'disposition':'Unresolved promotion-policy compatibility; no gate relaxed or profile changed','scope':'Static source/spec evidence only; no inference, endpoint comparison, speed or capability claim'}
print(json.dumps(result,indent=2))
