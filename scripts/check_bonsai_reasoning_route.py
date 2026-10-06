#!/usr/bin/env python3
"""AW-0103 read-only pinned-source reasoning-effort route screen."""
import hashlib,json,struct
from pathlib import Path
R=Path('/Users/chad/Models/agentwing/evidence/AW-0103');ROOT=Path(__file__).resolve().parents[1]
receipt=json.loads((R/'source-receipt.json').read_text())
for item in receipt:assert hashlib.sha256((R/Path(item['path']).name).read_bytes()).hexdigest()==item['sha256']
arg=(R/'arg.cpp').read_text();server=(R/'server-common.cpp').read_text();chat=(R/'chat.cpp').read_text();context=(R/'server-context.cpp').read_text()
provider=ROOT/'node_modules/@earendil-works/pi-coding-agent/dist/bundle/chunks/openai-completions-ERMU2SS7.js';text=provider.read_text()
config=json.loads((ROOT/'config/pi-bonsai-selective-models.json').read_text());entry=config['providers']['agentwing-bonsai'];assert entry['compat']['supportsReasoningEffort'] and entry['models'][0]['reasoning']
model=Path('/Users/chad/Models/agentwing/checkpoints/bonsai2-27b/Ternary-Bonsai-2-27B-PTQ1_0.gguf')
with model.open('rb') as f:header=f.read(16*1024*1024)
key=b'tokenizer.chat_template';p=header.find(key);assert p>=8 and struct.unpack_from('<Q',header,p-8)[0]==len(key);p+=len(key);assert struct.unpack_from('<I',header,p)[0]==8;n=struct.unpack_from('<Q',header,p+4)[0];template=header[p+12:p+12+n].decode();(R/'model-chat-template.jinja').write_text(template)
checks={'cli_sets_template_kwarg': 'params.default_template_kwargs["reasoning_effort"] = json(value).dump()' in arg,'server_uses_cli_kwargs':'params_base.default_template_kwargs' in context,'oai_body_overrides_kwarg':'inputs.chat_template_kwargs["reasoning_effort"] = json(reasoning_effort).dump()' in server,'jinja_extra_context_receives_kwargs':'params.extra_context[el.first] = json::parse(el.second)' in chat,'pi_generic_effort_forwarding':'params.reasoning_effort=model.thinkingLevelMap?.[options.reasoningEffort]??options.reasoningEffort' in text,'template_reads_effort':"reasoning_effort|default('xhigh')" in template,'template_accepts_medium':"('xhigh', 'medium', 'low')" in template,'profile_medium':json.loads((ROOT/'spec/bonsai-selective-local.json').read_text())['reasoning_effort']=='medium'}
assert all(checks.values())
result={'experiment':'AW-0103','static_route_checks_passed':True,'checks':checks,'sources':receipt,'provider_path':str(provider.relative_to(ROOT)),'provider_sha256':hashlib.sha256(provider.read_bytes()).hexdigest(),'template_sha256':hashlib.sha256(template.encode()).hexdigest(),'template_bytes':n,'models_config_sha256':hashlib.sha256((ROOT/'config/pi-bonsai-selective-models.json').read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'external_evidence':str(R),'interpretation':'Pinned source routes CLI/default and OAI medium into template context; no source evidence supporting a missing-medium patch','limitations':'Static conditional source-path screen, not capture of an actual rendered request or proof of token reduction. Template accepting low is syntactic and does not override publisher warning that low does not reduce thinking. No profile/effort/budget change.'}
(R/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
