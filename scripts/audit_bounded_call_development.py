#!/usr/bin/env python3
"""AW-0054 record/configuration/trace audit; coverage is a separate gate."""
import argparse
from collections import Counter
import json
from pathlib import Path
from audit_p2_development import audit
from audit_sampling_capture import receipt_ok
from audit_stage_a import METRIC
from run_local_agent import ROOT, digest


def decode_ids(ids, tokenizer_path):
    tokenizer=json.loads(tokenizer_path.read_text())
    assert tokenizer['decoder']['type']=='ByteLevel'
    vocab={v:k for k,v in tokenizer['model']['vocab'].items()}
    added={t['id']:t['content'] for t in tokenizer['added_tokens']}
    base=list(range(33,127))+list(range(161,173))+list(range(174,256))
    codes=base[:];extra=0
    for byte in range(256):
        if byte not in base:base.append(byte);codes.append(256+extra);extra+=1
    inverse={chr(code):byte for byte,code in zip(base,codes)}
    return b''.join(added[i].encode() if i in added else bytes(inverse[c] for c in vocab[i]) for i in ids).decode('utf-8')


def check(run):
    assert receipt_ok(run)
    plan_path=ROOT/'evidence/AW-0054-development-plan.json';plan=json.loads(plan_path.read_text())
    for path,expected in plan['hashes'].items():assert digest(path)==expected,path
    m=json.loads((run/'manifest.json').read_text());profile=json.loads((run/'candidate-plan.json').read_text())
    assert digest(run/'candidate-plan.json')==plan['candidate_profile_sha256']==m['candidate_plan_sha256']
    assert m['selection']==['dev-multi-file'] and m['profile']=='AW0054-bounded-calls'
    assert m['server_binary_sha256']==profile['server_binary_sha256']==plan['server_binary_sha256']
    assert not m['inherited_runtime_environment']
    for name,value in m['source_hashes'].items():assert digest(run/Path(name).name)==value==digest(ROOT/name)
    observer={'SWIFTLET_SAMPLING_TRACE':str(run/'sampling.jsonl')};assert m['observer_environment']==observer
    prefix=['/usr/bin/env',*[f'{k}={v}' for k,v in sorted({**profile['environment'],**observer}.items())],profile['server_binary']]
    assert m['server_command'][:len(prefix)]==prefix
    assert m['server_command'][-5:]==['--accept-schema-tags','--salvage-tool-prefix','--allow-repeated-ngrams','--stop-after-tool-call','--zero-frequency-penalty']
    assert m['task_timeout_seconds']==plan['task_timeout_seconds']==1800
    assert m['workspace_policy']['path']==plan['workspace']
    p=run/'dev-multi-file';assert digest(p/'system-prompt.txt')==profile['system_prompt_sha256']==m['system_prompt_sha256']
    settings=json.loads((ROOT/'spec/validated-local-agent.json').read_text())['settings']
    assert digest(p/'pi-models.json')==settings['pi_models_sha256']
    events=[json.loads(l) for l in (p/'pi.jsonl').read_text().splitlines() if l.strip()]
    assert [e['cwd'] for e in events if e.get('type')=='session']==[plan['workspace']]
    rows=[json.loads(l) for l in (run/'sampling.jsonl').read_text().splitlines() if l.strip()]
    groups=[];group=None
    for row in rows:
        if row['event']=='begin':
            assert group is None and row['request']==len(groups)+1
            group={'begin':row,'decisions':[]}
        elif row['event']=='decision':
            assert group is not None and row['request']==group['begin']['request'];group['decisions'].append(row)
        elif row['event']=='end':
            assert group is not None and row['request']==group['begin']['request']
            group['end']=row;groups.append(group);group=None
        else:raise AssertionError('unknown trace event')
    assert group is None and groups
    deps=json.loads((ROOT/'spec/dependencies.json').read_text());tokenizer=Path(deps['qwen3_6_35b_a3b_8bit_qpack']['local_path'])/'tokenizer.json'
    first_text=decode_ids(groups[0]['begin']['actual_prompt_ids'],tokenizer)
    assert (p/'system-prompt.txt').read_text().rstrip('\n') in first_text
    metrics=[m for l in (p/'server.log').read_text().splitlines() if (m:=METRIC.fullmatch(l))]
    assert len(metrics)==len(groups)
    previous=None;findings=[]
    for g,metric in zip(groups,metrics):
        b,end=g['begin'],g['end'];assert b['temperature']==b['frequency_penalty']==b['presence_penalty']==b['no_repeat_ngram']==0
        assert 0 < b['admitted_max_new'] <= 512 and b['actual_prompt_ids']==b['rendered_prompt_ids']
        assert len(b['actual_prompt_ids'])==b['new_prompt_tokens']+b['reused_prompt_tokens']
        if b['reused_prompt_tokens']:assert previous is not None and b['actual_prompt_ids'][:b['reused_prompt_tokens']]==previous and len(previous)==b['reused_prompt_tokens']
        counts=Counter();generated=[];anomalies=[]
        for index,d in enumerate(g['decisions']):
            t=d['selected'];assert d['generated_before']==len(generated) and d['seen_before']==counts[t]
            assert d['is_eos']==(t in b['eos_ids'])
            if d['raw']['nonfinite'] or d['selected_raw']!=d['selected_adjusted'] or d['adjusted']['top'][0]['id']!=t or t in b['suppressed_ids'] or (d['ban_eos'] and d['is_eos']):anomalies.append(index)
            if d['is_eos']:assert index==len(g['decisions'])-1
            else:generated.append(t);counts[t]+=1
        assert generated==end['generated_ids'] and len(generated)<=b['admitted_max_new']
        assert [b['new_prompt_tokens'],b['reused_prompt_tokens'],b['matched_prompt_tokens'],len(generated)]==[int(metric[i]) for i in [2,3,4,5]]
        previous=b['actual_prompt_ids']+generated if end['cached_tokens_after'] else None
        if previous:assert len(previous)==end['cached_tokens_after']
        findings.append({'request':b['request'],'generated_tokens':len(generated),'finish_reason':end['finish_reason'],'sampling_anomalies':anomalies})
    integrity=audit(run)
    return {'run':str(run),'raw_receipt_sha256':digest(run/'sha256-recursive.json'),'plan_sha256':digest(plan_path),
        'configuration_and_prompt_trace_checks_passed':True,'tokenizer_sha256':digest(tokenizer),'integrity':integrity,
        'requests':findings,'passed':integrity['passed'] and all(not f['sampling_anomalies'] for f in findings),
        'scope':'Record/prompt/sampling/grader audit only. Added regression coverage and actual validation require separate review; no promotion claim.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);args=p.parse_args();result=check(args.run)
    print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
