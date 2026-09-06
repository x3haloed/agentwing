#!/usr/bin/env python3
"""Terminal AW-0053 integrity/prefix audit; protocol/content review is separate."""
import argparse
import copy
import json
from pathlib import Path
from audit_sampling_capture import receipt_ok
from audit_sampling_replay import audit_trace
from run_local_agent import digest


def audit(run):
    assert receipt_ok(run)
    plan=json.loads((run/'plan.json').read_text());manifest=json.loads((run/'manifest.json').read_text())
    assert manifest['plan_sha256']==digest(run/'plan.json') and manifest['runtime_revision']==plan['runtime_revision']
    for path,expected_hash in plan['hashes'].items():assert digest(path)==expected_hash,path
    assert digest(run/'probe_output_budget.py')==next(v for k,v in plan['hashes'].items() if k.endswith('/scripts/probe_output_budget.py'))
    source=Path(plan['source_run']);assert receipt_ok(source)
    assert digest(source/'sha256-recursive.json')==plan['source_receipt_sha256']
    assert digest(run/'input.json')==plan['hashes'][plan['input']]
    original_input=json.loads((run/'input.json').read_text());expected=copy.deepcopy(original_input)
    expected['admitted_max_new']=1024
    p=run/'A1';trace=[json.loads(l) for l in (p/'sampling.jsonl').read_text().splitlines()]
    result=audit_trace(trace,expected,0)
    reference=[json.loads(l) for l in (source/'A1/sampling.jsonl').read_text().splitlines()]
    old_decisions=[d for d in reference if d['event']=='decision'];new_decisions=trace[1:-1]
    keys=['selected','seen_before','selected_raw','selected_adjusted','raw','adjusted','ban_eos','is_eos']
    prefix_matches=len(new_decisions)>=512 and len(old_decisions)==512 and all(
        all(a[k]==b[k] for k in keys) for a,b in zip(new_decisions[:512],old_decisions))
    assert reference[0]['actual_prompt_ids']==trace[0]['actual_prompt_ids']
    assert trace[-1]['generated_ids'][:512]==reference[-1]['generated_ids'] or not prefix_matches
    report=json.loads((p/'report.json').read_text());record=json.loads((p/'result.json').read_text())
    assert report['text']==trace[-1]['text'] and report['generated_tokens']==len(trace[-1]['generated_ids'])
    assert report['requested_max_new']==1024 and report['frequency_penalty']==0 and report['tools_executed'] is False
    assert report['prompt_tokens']==2219 and report['reused_prompt_tokens']==0
    launch=json.loads((p/'launch.json').read_text())
    assert launch['command']==[plan['testing_helper'],'--test-bundle-path',plan['test_binary'],
        '--filter','OutputBudgetTests',plan['test_binary'],'--testing-library','swift-testing']
    assert launch['environment']=={**plan['environment'],'AW53_QPACK_DIR':plan['model'],
        'AW53_INPUT':str(run/'input.json'),'AW53_OUTPUT':str(p/'report.json'),'AW53_FREQUENCY':'0',
        'SWIFTLET_SAMPLING_TRACE':str(p/'sampling.jsonl')}
    assert record['error']==(None if prefix_matches else 'extended-budget-prefix-does-not-match-zero-penalty-reference')
    assert record['exit']==0
    samples=[json.loads(l) for l in (p/'pressure.jsonl').read_text().splitlines()]
    assert samples and all(a[0]<=b[0] for a,b in zip(samples,samples[1:]))
    peak=max(r[1] for r in samples);growth=max(r[2]-record['swap_baseline_mib'] for r in samples)
    assert peak==record['peak_pressure'] and growth==record['peak_swap_growth_mib']
    summary=json.loads((run/'summary.json').read_text());assert summary['arms']==[record]
    assert summary['sequence_complete']==prefix_matches
    result.update(run=str(run),receipt_sha256=digest(run/'sha256-recursive.json'),
        record_integrity_passed=True,prefix_512_tokens_and_observed_scores_match=prefix_matches,
        host_gates_pass=peak<4 and growth<=1024,wall_seconds=record['wall_seconds'],
        complete_protocol_and_useful_coverage='requires separate frozen-parser and content review',
        scope='No endpoint utility or promotion claim. Audit assumes terminal report exists; interrupted attempts need separate failure audit.')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);args=p.parse_args()
    print(json.dumps(audit(args.run),indent=2))
