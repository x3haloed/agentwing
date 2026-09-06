#!/usr/bin/env python3
"""Audit terminal AW-0052 records; separate reproduction from candidate content."""
import argparse
from collections import Counter
import json
from pathlib import Path
from audit_sampling_capture import receipt_ok, f32, finite
from run_local_agent import digest


def audit_trace(trace, expected_input, frequency):
    assert len(trace)>=2 and trace[0]['event']=='begin' and trace[-1]['event']=='end'
    b,end=trace[0],trace[-1];decisions=trace[1:-1]
    assert b['request']==end['request']==1
    assert all(d['event']=='decision' and d['request']==1 for d in decisions)
    assert b['actual_prompt_ids']==expected_input['actual_prompt_ids']==b['rendered_prompt_ids']
    assert b['new_prompt_tokens']==len(b['actual_prompt_ids']) and b['reused_prompt_tokens']==b['matched_prompt_tokens']==0
    for key in ['temperature','presence_penalty','no_repeat_ngram','min_new','top_k','top_p','eos_ids','suppressed_ids','stop_sequences','stop_after_sequences','admitted_max_new']:
        assert b[key]==expected_input[key],key
    assert b['frequency_penalty']==frequency and b['greedy_observation_supported']
    counts=Counter();generated=[];anomalies=[];deviations=[]
    for i,d in enumerate(decisions):
        token=d['selected']
        assert d['generated_before']==len(generated) and d['seen_before']==counts[token]
        assert d['is_eos']==(token in b['eos_ids'])
        if len(generated)<b['min_new']:assert d['ban_eos']
        if len(generated)>=max(300,b['min_new']):assert not d['ban_eos']
        if len(generated)>=b['min_new'] and d['raw']['top'][0]['id'] in b['eos_ids']:assert not d['ban_eos']
        # Before 300, the remaining EOS condition depends on decoded visible punctuation/newline.
        if token in b['suppressed_ids'] or (d['ban_eos'] and d['is_eos']):anomalies.append([i,'mask'])
        if d['raw']['nonfinite']:anomalies.append([i,'raw-nonfinite'])
        if not d['adjusted']['top'] or d['adjusted']['top'][0]['id']!=token:anomalies.append([i,'argmax'])
        if finite(d['selected_raw']) and finite(d['selected_adjusted']):
            penalty=f32(f32(b['presence_penalty'])+f32(f32(frequency)*f32(counts[token])))
            if f32(d['selected_raw']-penalty)!=d['selected_adjusted']:anomalies.append([i,'score-arithmetic'])
        else:anomalies.append([i,'selected-nonfinite'])
        if d['raw']['top'][0]['id']!=token:deviations.append(i)
        if d['is_eos']:assert i==len(decisions)-1
        else:generated.append(token);counts[token]+=1
    assert generated==end['generated_ids'] and len(generated)<=b['admitted_max_new']
    assert end['cached_tokens_after'] in [0,len(b['actual_prompt_ids'])+len(generated)]
    ngrams=Counter(tuple(generated[i:i+8]) for i in range(max(0,len(generated)-7)))
    return {'trace_integrity_passed':True,'decisions':len(decisions),'generated_tokens':len(generated),
        'finish_reason':end['finish_reason'],'sampling_anomalies':anomalies,'raw_winner_changes':deviations,
        'repeated_8gram_occurrences':sum(n-1 for n in ngrams.values())}


def audit(run):
    assert receipt_ok(run)
    plan=json.loads((run/'plan.json').read_text());manifest=json.loads((run/'manifest.json').read_text())
    assert digest(run/'plan.json')==manifest['plan_sha256']
    assert manifest['runtime_revision']==plan['runtime_revision']
    assert digest(run/'probe_sampling_replay.py')==next(v for k,v in plan['hashes'].items() if k.endswith('/scripts/probe_sampling_replay.py'))
    source=Path(plan['source_run']);assert receipt_ok(source)
    assert digest(source/'sha256-recursive.json')==plan['source_receipt_sha256']
    expected=json.loads((run/'input.json').read_text());assert digest(run/'input.json')==plan['hashes'][plan['input']]
    reference=[json.loads(line) for line in (source/'sampling.jsonl').read_text().splitlines()]
    assert expected==next(row for row in reference if row['event']=='begin' and row['request']==13)
    original=next(row for row in reference if row['event']=='end' and row['request']==13)
    summary=json.loads((run/'summary.json').read_text());rows=[]
    for index,record in enumerate(summary['arms']):
        label,frequency=plan['order'][index];assert [record['arm'],record['frequency_penalty']]==[label,frequency]
        directory=run/label;assert json.loads((directory/'result.json').read_text())==record
        launch=json.loads((directory/'launch.json').read_text())
        assert launch['command']==[plan['testing_helper'],'--test-bundle-path',plan['test_binary'],
             '--filter','SamplingReplayTests',plan['test_binary'],'--testing-library','swift-testing']
        assert launch['environment']=={**plan['environment'],'AW52_QPACK_DIR':plan['model'],
            'AW52_INPUT':str(run/'input.json'),'AW52_OUTPUT':str(directory/'report.json'),
            'AW52_FREQUENCY':'0.5' if frequency==0.5 else '0','SWIFTLET_SAMPLING_TRACE':str(directory/'sampling.jsonl')}
        samples=[json.loads(line) for line in (directory/'pressure.jsonl').read_text().splitlines()]
        assert samples and all(a[0]<=b[0] for a,b in zip(samples,samples[1:]))
        pressure=max(s[1] for s in samples);growth=max(s[2]-record['swap_baseline_mib'] for s in samples)
        assert pressure==record['peak_pressure'] and growth==record['peak_swap_growth_mib']
        row={'arm':label,'record_error':record['error'],'host_gates_pass':pressure<4 and growth<=1024,
             'wall_seconds':record['wall_seconds'],'trace_complete':False}
        if (directory/'report.json').exists():
            trace=[json.loads(line) for line in (directory/'sampling.jsonl').read_text().splitlines()]
            row.update(audit_trace(trace,expected,frequency));row['trace_complete']=True
            report=json.loads((directory/'report.json').read_text());end=trace[-1]
            assert report['text']==end['text'] and report['generated_tokens']==len(end['generated_ids'])
            assert report['frequency_penalty']==frequency and report['tools_executed'] is False
            equal=end['generated_ids']==original['generated_ids'] and end['text']==original['text']
            row['matches_cached_reference']=equal
            row['first_generated_difference']=next((i for i,(a,b) in enumerate(zip(end['generated_ids'],original['generated_ids'])) if a!=b),None)
            if label.startswith('C'):
                assert record['error']==(None if equal else 'fresh-prefill-control-does-not-reproduce-cached-failure')
        if record['error']:assert index==len(summary['arms'])-1
        rows.append(row)
    assert summary['sequence_complete']==(len(rows)==3 and all(r['record_error'] is None for r in rows))
    return {'run':str(run),'receipt_sha256':digest(run/'sha256-recursive.json'),'record_integrity_passed':True,
        'sequence_complete':summary['sequence_complete'],'arms':rows,
        'scope':'Trace and record audit only. A complete valid tool call and requested coverage require independent review; no endpoint or promotion claim.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args()
    print(json.dumps(audit(args.run),indent=2))

if __name__=='__main__':main()
