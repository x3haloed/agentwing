#!/usr/bin/env python3
"""Audit AW-0056 sealed source-stage fidelity; no endpoint claims."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path('/Users/chad/Models/agentwing/evidence/AW-0037/20260906T063224.469387Z')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def receipt(run):
    entries = json.loads((run/'sha256.json').read_text())
    actual = {str(p.relative_to(run)) for p in run.rglob('*') if p.is_file() and p.name != 'sha256.json'}
    assert actual == set(entries)
    for rel, value in entries.items():
        path = run/rel
        assert path.resolve().is_relative_to(run.resolve()) and not path.is_symlink()
        assert digest(path) == value, rel
    return digest(run/'sha256.json')

def floats(path, count):
    data = path.read_bytes()
    assert len(data) == count*4
    values = struct.unpack('<' + str(count) + 'f', data)
    assert all(math.isfinite(x) for x in values)
    return values

def relative(a, b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b))/max(sum(y*y for y in b),1e-30))

def audit(run):
    sealed = receipt(run)
    reference_receipt = receipt(REFERENCE)
    manifest = json.loads((run/'manifest.json').read_text())
    assert manifest['reference_receipt_sha256'] == reference_receipt
    plan = json.loads((ROOT/'evidence/AW-0056-screen-plan.json').read_text())
    for local, archived in [('probes/expert_sixbit.m','expert_sixbit.m'), ('scripts/probe_expert_sixbit.py','probe_expert_sixbit.py')]:
        assert digest(run/archived) == plan['pins'][local]
    assert digest(run/'expert_sixbit') == manifest['binary_sha256']
    assert digest(run/'Kernels.metal.txt') == manifest['kernel_sha256'] == plan['pins']['/Users/chad/Models/agentwing/dependencies/Swiftlet/Sources/SwiftletCore/Kernels.metal.txt']
    assert (run/'fixtures.json').read_bytes() == (REFERENCE/'fixtures.json').read_bytes()
    rows = [json.loads(s) for s in (run/'results.jsonl').read_text().splitlines()]
    refs = [json.loads(s) for s in (REFERENCE/'results.jsonl').read_text().splitlines()]
    assert len(rows) == len(refs) == 72
    mixtures, experts, implementations = [], [], []
    by_layer = {}
    for index, (row, ref) in enumerate(zip(rows, refs)):
        assert row['fixture'] == ref['fixture'] == index
        assert row['layer'] == ref['layer']
        assert len(row['experts']) == len(ref['experts']) == 8
        for entry, original in zip(row['experts'],ref['experts']):
            for key in ['expert','source_sha256','stages_file']:
                assert entry[key] == original[key]
            path = run/'stages'/entry['stages_file']
            assert digest(path) == entry['stages_sha256']
            a = floats(path,3584)
            b = floats(REFERENCE/'stages'/original['stages_file'],3584)
            for key,lo,hi in [('gate',0,512),('up',512,1024),('silu',1024,1536),('down',1536,3584)]:
                value = relative(a[lo:hi],b[lo:hi])
                assert math.isclose(value,entry[key+'_fidelity_l2'],rel_tol=1e-10,abs_tol=1e-12)
            experts.append(relative(a[1536:],b[1536:]))
            implementations.extend([entry['projection_relative_l2'],entry['silu_relative_l2']])
            assert entry['candidate_bytes'] == plan['candidate_bytes']
        path = run/'stages'/row['mixture_file']
        assert digest(path) == row['mixture_sha256']
        value = relative(floats(path,2048),floats(REFERENCE/'stages'/ref['mixture_file'],2048))
        assert math.isclose(value,row['mixture_fidelity_l2'],rel_tol=1e-10,abs_tol=1e-12)
        mixtures.append(value)
        by_layer.setdefault(row['layer'],[]).append(value)
        implementations.append(row['mixture_relative_l2'])
    assert max(implementations) <= plan['implementation_relative_l2_max']
    result = json.loads((run/'result.json').read_text())
    assert result['exit'] == 0 and result['error'] is None
    samples = result['pressure_samples']
    assert samples and max(s[1] for s in samples) < 4
    growth = max(s[2]-result['swap_baseline_mib'] for s in samples)
    assert growth <= 1024
    passed = max(mixtures)<=plan['mixture_relative_l2_max'] and max(experts)<=plan['expert_down_relative_l2_max']
    return dict(run=str(run),raw_receipt_sha256=sealed,record_and_stage_audit_passed=True,fixtures=len(rows),expert_executions=len(experts),maximum_mixture_relative_l2=max(mixtures),maximum_expert_down_relative_l2=max(experts),mixtures_exceeding_gate=sum(x>.05 for x in mixtures),experts_exceeding_gate=sum(x>.1 for x in experts),maximum_implementation_relative_l2=max(implementations),by_layer_max={k:max(v) for k,v in by_layer.items()},candidate_bytes=plan['candidate_bytes'],source_bytes=plan['source_bytes'],size_ratio=plan['candidate_bytes']/plan['source_bytes'],max_pressure=max(s[1] for s in samples),max_swap_growth_mib=growth,wall_seconds=result['wall_seconds'],numerical_continuation_gate_passed=passed,disposition='retained-for-deeper-validation' if passed else 'rejected-exact-midpoint-form',scope='Source fixed-route numerical screen using expanded q8, not packed execution, uncommon-route coverage, accumulated behavior, throughput or agent capability.')

if __name__ == '__main__':
    print(json.dumps(audit(Path(sys.argv[1])),indent=2))
