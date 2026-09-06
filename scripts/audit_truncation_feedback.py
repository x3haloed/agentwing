#!/usr/bin/env python3
"""AW-0055 terminal evidence/input/trace audit, independent of output acceptance."""
import argparse
import json
from pathlib import Path
from audit_sampling_capture import receipt_ok
from audit_sampling_replay import audit_trace
from audit_bounded_call_development import decode_ids
from run_local_agent import digest


def audit(run):
    assert receipt_ok(run)
    plan=json.loads((run/'plan.json').read_text());manifest=json.loads((run/'manifest.json').read_text())
    assert digest(run/'plan.json')==manifest['plan_sha256'] and manifest['runtime_revision']==plan['runtime_revision']
    for path,expected_hash in plan['hashes'].items():assert digest(path)==expected_hash,path
    assert digest(run/'probe_truncation_feedback.py')==next(v for k,v in plan['hashes'].items() if k.endswith('/scripts/probe_truncation_feedback.py'))
    source=Path(plan['source_run']);assert receipt_ok(source)
    assert digest(source/'sha256-recursive.json')==plan['source_receipt_sha256']
    original=[json.loads(l) for l in (source/'sampling.jsonl').read_text().splitlines()]
    b=next(r for r in original if r['event']=='begin' and r['request']==12)
    end=next(r for r in original if r['event']=='end' and r['request']==12)
    prefix=b['actual_prompt_ids']+end['generated_ids']
    expected=json.loads((run/'input.json').read_text());assert digest(run/'input.json')==plan['hashes'][plan['input']]
    assert len(end['generated_ids'])==512 and len(prefix)==plan['original_prefix_tokens']==2807
    assert expected['actual_prompt_ids']==prefix+expected['diagnostic_feedback_ids']
    assert len(expected['diagnostic_feedback_ids'])==plan['feedback_suffix_tokens']==80
    assert len(expected['actual_prompt_ids'])==plan['prepared_prompt_tokens']==2887
    feedback=Path(plan['feedback']).read_text().strip();assert expected['diagnostic_feedback_text']==feedback
    tokenizer=Path(plan['model'])/'tokenizer.json'
    suffix=decode_ids(expected['diagnostic_feedback_ids'],tokenizer)
    assert suffix=='<|im_end|>\n<|im_start|>user\n'+feedback+'<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'
    p=run/'A1';trace=[json.loads(l) for l in (p/'sampling.jsonl').read_text().splitlines()]
    findings=audit_trace(trace,expected,0)
    report=json.loads((p/'report.json').read_text());record=json.loads((p/'result.json').read_text())
    assert report['text']==trace[-1]['text'] and report['generated_tokens']==len(trace[-1]['generated_ids'])
    assert report['prompt_tokens']==2887 and report['reused_prompt_tokens']==0 and report['frequency_penalty']==0 and report['tools_executed'] is False
    launch=json.loads((p/'launch.json').read_text())
    assert launch['command']==[plan['testing_helper'],'--test-bundle-path',plan['test_binary'],'--filter','SamplingReplayTests',plan['test_binary'],'--testing-library','swift-testing']
    assert launch['environment']=={**plan['environment'],'AW52_QPACK_DIR':plan['model'],'AW52_INPUT':str(run/'input.json'),
        'AW52_OUTPUT':str(p/'report.json'),'AW52_FREQUENCY':'0','SWIFTLET_SAMPLING_TRACE':str(p/'sampling.jsonl')}
    samples=[json.loads(l) for l in (p/'pressure.jsonl').read_text().splitlines()]
    assert samples and all(a[0]<=b[0] for a,b in zip(samples,samples[1:]))
    peak=max(r[1] for r in samples);growth=max(r[2]-record['swap_baseline_mib'] for r in samples)
    assert peak==record['peak_pressure'] and growth==record['peak_swap_growth_mib']
    assert record['error'] is None and record['exit']==0
    summary=json.loads((run/'summary.json').read_text());assert summary['arms']==[record] and summary['sequence_complete']
    findings.update(run=str(run),receipt_sha256=digest(run/'sha256-recursive.json'),record_integrity_passed=True,
        captured_prefix_preserved=True,feedback_suffix_decoded_and_verified=True,host_gates_pass=peak<4 and growth<=1024,
        wall_seconds=record['wall_seconds'],complete_protocol_and_useful_progress='requires separate frozen-parser/content review',
        scope='Model-only recovery diagnostic. No partial tool execution, endpoint utility or live-cache equivalence claimed; interrupted attempts require separate failure audit.')
    return findings

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);args=p.parse_args()
    print(json.dumps(audit(args.run),indent=2))
