"""AW-0033 small exact-codec screen; no model or full bank conversion."""
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import zlib
from run_local_agent import preflight, host_sample, check_sample
from probe_expert_residency import MODEL


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    preflight()
    root = Path('/Users/chad/Models/agentwing/evidence/AW-0033')
    root.mkdir(exist_ok=True)
    run = root / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run.mkdir()
    trace_root = Path('/Users/chad/Models/agentwing/evidence/AW-0031/20260905T183732Z')
    trace = trace_root / 'T1/experts.jsonl'
    assert sha(trace) == json.loads((trace_root / 'sha256.json').read_text())['T1/experts.jsonl']
    events = [json.loads(x) for x in trace.read_text().splitlines()]
    model = Path(MODEL)
    layout = json.loads((model / 'packed_experts/layout.json').read_text())
    stride = layout['expertStride']
    assert stride == 3342336
    sample_ids = []
    for layer in [0, 20, 39]:
        counts = Counter(e for r in events if r['event'] == 'route' and r['layer'] == layer for e in r['experts'])
        ordered = sorted(counts, key=lambda e: (counts[e], e))
        sample_ids += [(layer, e, counts[e]) for e in ordered[:2] + ordered[-2:]]
    (run / 'selection.json').write_text(json.dumps(sample_ids) + '\n')
    baseline = host_sample()[1]
    samples, rows = [], []
    for layer, expert, count in sample_ids:
        reading = host_sample(); check_sample(reading, baseline); samples.append(reading)
        with (model / f'packed_experts/layer_{layer:02d}.bin').open('rb') as f:
            f.seek(expert * stride); raw = f.read(stride)
        assert len(raw) == stride
        for mode in ['raw', 'even-odd']:
            transformed = raw if mode == 'raw' else raw[::2] + raw[1::2]
            packed = zlib.compress(transformed, 1)
            restored = zlib.decompress(packed)
            if mode != 'raw':
                decoded = bytearray(stride); decoded[::2] = restored[:stride//2]; decoded[1::2] = restored[stride//2:]; restored = decoded
            assert restored == raw
            rows.append({'layer': layer, 'expert': expert, 'trace_occurrences': count, 'mode': mode, 'source_sha256': hashlib.sha256(raw).hexdigest(), 'compressed_sha256': hashlib.sha256(packed).hexdigest(), 'source_bytes': stride, 'compressed_bytes': len(packed), 'page_aligned_ratio': ((len(packed)+16383)//16384*16384)/stride, 'roundtrip_passed': True})
    metadata = sum(s['size'] for s in layout['sections'] if not s['name'].endswith('.weight'))
    weights = sum(s['size'] for s in layout['sections'] if s['name'].endswith('.weight'))
    trace_result = json.loads(Path('evidence/AW-0031-routing-results.json').read_text())
    wall = sum(trace_result['arms'][1]['metrics'][p]['wall'] for p in ['prefill', 'decode'])
    fraction = trace_result['read_batch_seconds'] / wall
    result = {'run': str(run), 'scope': 'Deterministic 12-expert sample, one short route trace, exact zlib-1 size screen only', 'source_model': MODEL, 'trace_sha256': sha(trace), 'layout_sha256': sha(model / 'packed_experts/layout.json'), 'script_sha256': sha(__file__), 'zlib_version': zlib.ZLIB_RUNTIME_VERSION, 'os': subprocess.check_output(['sw_vers'], text=True), 'hardware': subprocess.check_output(['sysctl', 'hw.model', 'hw.memsize'], text=True), 'pressure_samples': samples, 'swap_baseline_mib': baseline, 'rows': rows, 'layout': {'weight_bytes': weights, 'scale_bias_bytes': metadata, 'padding_bytes': stride-weights-metadata}, 'diagnostic_amdahl': {'source': 'AW-0031 T1, traced model steps; not end-to-end agent wall', 'read_fraction': fraction, 'half_read_time_speedup': 1/(1-fraction*.5), 'read_time_ratio_needed_for_1_25x': 1-.2/fraction, 'hypothetical_four_bit_same_metadata_size_ratio': (weights*.5+metadata)/stride, 'limits': 'Assumes fixed non-read time and proportional read time, no decompression overhead or memory/execution changes; not a prediction or universal bound'}}
    (run / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    (run / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    (run / 'sha256.json').write_text(json.dumps({p.name: sha(p) for p in run.iterdir() if p.is_file() and p.name != 'sha256.json'}, indent=2) + '\n')
    print(run)
    print(json.dumps({mode: {'min_ratio': min(r['page_aligned_ratio'] for r in rows if r['mode']==mode), 'max_ratio': max(r['page_aligned_ratio'] for r in rows if r['mode']==mode)} for mode in ['raw', 'even-odd']}, indent=2))
    print(json.dumps(result['diagnostic_amdahl'], indent=2))


if __name__ == '__main__':
    main()
