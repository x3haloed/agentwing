#!/usr/bin/env python3
"""Audit AW-0051 trace integrity separately from numerical/behavior findings."""
import argparse
import ast
from collections import Counter
import copy
import json
import math
from pathlib import Path
import struct
from audit_p2_development import audit
from audit_stage_a import METRIC
from run_local_agent import ROOT, digest


def receipt_ok(run):
    receipt=json.loads((run/'sha256-recursive.json').read_text())
    return receipt=={str(p.relative_to(run)):digest(p) for p in run.rglob('*')
        if p.is_file() and not p.is_symlink() and p.name!='sha256-recursive.json'}


def visible(run,task):
    result=[]
    for line in (run/task/'pi.jsonl').read_text().splitlines():
        e=json.loads(line)
        if e.get('type')=='message_end' and e.get('message',{}).get('role')=='assistant':
            content=copy.deepcopy(e['message']['content'])
            for block in content:
                if block.get('type')=='toolCall':block.pop('id',None)
            result.append({'kind':'assistant','content':content})
        elif e.get('type')=='tool_execution_end':
            result.append({'kind':'tool_result','result':e.get('result'),'isError':bool(e.get('isError'))})
    return result


def rejected_text(run,task):
    for line in reversed((run/task/'server.log').read_text().splitlines()):
        if ' rejected tool output: ' in line:
            value=line.split(' rejected tool output: ',1)[1]
            try:return json.loads(value)
            except json.JSONDecodeError:
                try:return ast.literal_eval(value)
                except (ValueError,SyntaxError):return None
    return None


def f32(value):return struct.unpack('f',struct.pack('f',value))[0]
def finite(value):return isinstance(value,(int,float)) and math.isfinite(value)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args();run=args.run
    plan_path=ROOT/'evidence/AW-0051-sampling-capture-plan.json'
    plan=json.loads(plan_path.read_text());task=plan['task'];reference=Path(plan['reference_run'])
    assert receipt_ok(run) and receipt_ok(reference)
    assert digest(reference/'sha256-recursive.json')==plan['reference_receipt_sha256']
    integrity=audit(run);assert integrity['passed'],integrity
    m=json.loads((run/'manifest.json').read_text());refm=json.loads((reference/'manifest.json').read_text())
    profile=json.loads((run/'candidate-plan.json').read_text())
    assert digest(run/'candidate-plan.json')==plan['candidate_plan_sha256']==digest(ROOT/plan['candidate_plan'])
    assert digest(run/Path(plan['runner']).name)==plan['runner_sha256']==m['source_hashes'][plan['runner']]
    assert m['source_hashes']['scripts/stable_workspace.py']==plan['workspace_helper_sha256']==digest(run/'stable_workspace.py')
    assert m['workspace_policy']==plan['workspace_policy'] and m['selection']==[task]
    assert m['corpus_receipt_sha256']==plan['corpus_receipt_sha256'] and not m['inherited_runtime_environment']
    assert m['server_binary_sha256']==profile['server_binary_sha256']
    observer={'SWIFTLET_SAMPLING_TRACE':str(run/'sampling.jsonl')}
    assert m['observer_environment']==observer
    prefix=['/usr/bin/env',*[f'{k}={v}' for k,v in sorted({**profile['environment'],**observer}.items())],profile['server_binary']]
    assert m['server_command'][:len(prefix)]==prefix
    old_profile=json.loads((reference/'candidate-plan.json').read_text())
    assert profile['environment']==old_profile['environment']
    assert m['server_command'][len(prefix):]==refm['server_command'][len(old_profile['environment'])+2:]
    for name in ['system-prompt.txt','pi-models.json','task.txt']:
        assert digest(run/task/name)==digest(reference/task/name)
    events=[json.loads(line) for line in (run/task/'pi.jsonl').read_text().splitlines() if line.strip()]
    assert [e['cwd'] for e in events if e.get('type')=='session']==[plan['workspace_policy']['path']]
    metrics=[match for line in (run/task/'server.log').read_text().splitlines() if (match:=METRIC.fullmatch(line))]
    trace=[json.loads(line) for line in (run/'sampling.jsonl').read_text().splitlines() if line.strip()]
    groups=[];active=None
    for row in trace:
        if row['event']=='begin':
            assert active is None and row['request']==len(groups)+1
            active={'begin':row,'decisions':[]}
        elif row['event']=='decision':
            assert active and row['request']==active['begin']['request'];active['decisions'].append(row)
        elif row['event']=='end':
            assert active and row['request']==active['begin']['request']
            active['end']=row;groups.append(active);active=None
        else:raise AssertionError('Unknown trace event')
    assert active is None and len(groups)==len(metrics)>0
    findings=[];previous=None
    for group,metric in zip(groups,metrics):
        b=group['begin'];end=group['end'];decisions=group['decisions']
        assert b['temperature']==0 and b['greedy_observation_supported'] and b['no_repeat_ngram']==0
        assert b['admitted_max_new']==512 and b['frequency_penalty']==0.5 and b['presence_penalty']==0
        assert [b['new_prompt_tokens'],b['reused_prompt_tokens'],b['matched_prompt_tokens'],len(end['generated_ids'])]==[int(metric[i]) for i in [2,3,4,5]]
        assert len(b['actual_prompt_ids'])==b['new_prompt_tokens']+b['reused_prompt_tokens']
        assert b['actual_prompt_ids']==b['rendered_prompt_ids']
        if b['reused_prompt_tokens']:
            assert previous is not None and b['reused_prompt_tokens']==len(previous)
            assert b['actual_prompt_ids'][:len(previous)]==previous
        if end['cached_tokens_after']:
            previous=b['actual_prompt_ids']+end['generated_ids'];assert len(previous)==end['cached_tokens_after']
        else:previous=None
        counts=Counter();generated=[];score_bad=[];argmax_bad=[];mask_bad=[];raw_anomalies=[];deviations=[]
        for i,d in enumerate(decisions):
            token=d['selected'];assert d['generated_before']==len(generated) and d['seen_before']==counts[token]
            if token in b['suppressed_ids'] or (d['ban_eos'] and token in b['eos_ids']):mask_bad.append(i)
            assert d['is_eos']==(token in b['eos_ids'])
            top=d['adjusted']['top'];rawtop=d['raw']['top']
            if not top or top[0]['id']!=token:argmax_bad.append(i)
            if d['raw']['nonfinite']:raw_anomalies.append(i)
            if rawtop and rawtop[0]['id']!=token:deviations.append(i)
            if finite(d['selected_raw']) and finite(d['selected_adjusted']):
                penalty=f32(f32(b['presence_penalty'])+f32(f32(b['frequency_penalty'])*f32(counts[token])))
                if f32(d['selected_raw']-penalty)!=d['selected_adjusted']:score_bad.append(i)
            if d['is_eos']:assert i==len(decisions)-1
            else:generated.append(token);counts[token]+=1
        assert generated==end['generated_ids']
        ngrams=Counter(tuple(generated[i:i+8]) for i in range(max(0,len(generated)-7)))
        findings.append({'request':b['request'],'generated_tokens':len(generated),'finish_reason':end['finish_reason'],
            'raw_nonfinite_decisions':raw_anomalies,'selected_score_arithmetic_mismatches':score_bad,
            'selected_argmax_mismatches':argmax_bad,'selected_mask_violations':mask_bad,
            'raw_winner_differs_count':len(deviations),'first_raw_winner_differences':deviations[:20],
            'repeated_8gram_occurrences':sum(n-1 for n in ngrams.values()),
            'finite_raw_logit_min':min((d['raw']['finite_min'] for d in decisions if finite(d['raw']['finite_min'])),default=None),
            'finite_raw_logit_max':max((d['raw']['finite_max'] for d in decisions if finite(d['raw']['finite_max'])),default=None)})
    current_visible=visible(run,task);old_visible=visible(reference,task)
    raw_ref=rejected_text(reference,task);raw_current=rejected_text(run,task)
    summary=json.loads((run/'summary.json').read_text());oldsummary=json.loads((reference/'summary.json').read_text())
    result={'run':str(run),'raw_receipt_sha256':digest(run/'sha256-recursive.json'),'plan_sha256':digest(plan_path),
        'record_and_trace_integrity_passed':True,'integrity':integrity,'request_count':len(groups),
        'decisions':sum(len(g['decisions']) for g in groups),'requests':findings,
        'structured_visible_trajectory_equal':current_visible==old_visible,
        'reference_rejection_text_decoded':isinstance(raw_ref,str),
        'rejected_output_equal':raw_ref==raw_current if isinstance(raw_ref,str) else None,
        'last_trace_text_matches_rejected_output':groups[-1]['end']['text']==raw_current if isinstance(raw_current,str) else None,
        'utility':[oldsummary['utility'],summary['utility']],
        'limits':['Integrity success does not assert numerical invariants or behavior equality; findings are separate',
                  'Top candidates are bounded; full logit tensors and hidden states were not captured',
                  'Repeated n-grams describe output and are not an acceptance gate or a proposed restriction',
                  'Observer timing is not performance evidence; no failure is repaired or rescored']}
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
