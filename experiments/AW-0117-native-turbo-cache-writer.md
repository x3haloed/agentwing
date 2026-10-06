# AW-0117 — Native Turbo cache writer

## Status and hypothesis

Retained. Unchanged Atomic Metal Turbo3/4 SET_ROWS writers encode complete real
Bonsai populated V rows at layers3/31/63 into CPU-compatible cache blocks,
correctly follow reversed destination indices and preserve boundary canaries.

## Frozen configuration and acceptance

External plan pins harness, Swift runner, executable, complete unchanged Atomic
Metal library, AW-0109 captured authority, AW-0110 CPU packed authority and all
input/index/argument hashes. CPU decoder hash independently verified against
frozen AW-0105 and included in evidence receipt. Source Atomic
074bf826e1b06005a51737d29387e36657f41bf7; capture/model/Prism runtime/context/
sampling provenance inherited AW-0109. No new model inference, task, tool,
permission, sampler or chat-effort changes. Internal SSD, M1 Macmini9,1/16GB,
macOS27.0.1/26A434.

Four heads×48 populated positions,256 values/row.192 rows per case, two128
blocks per row,100/136 packed bytes for Turbo3/4. Input is real FP16 cache
converted to F32; inactive slots excluded. Destination indices191..0 challenge
row mapping, not just sequential memcpy. Native ABI fields extracted from
pinned struct: nk0=2,ne01=192,ne11/ne12=1, source row stride1024, i64 indices,
packed row stride100/136.192×1×1 threadgroups with32×1×1 threads. Prefix and
suffix256-byte canaries around cache destination. Runtime Metal3.0 compilation,
command completion checked,90s watchdog/.25s host pressure/swap checks.

Primary predeclared acceptance: all reconstructed outputs finite and relative
L2<=.005 against CPU encoding at reversed indices, all canaries unchanged.
Exact bytes diagnostic only; no model quality or speed acceptance.
`python3 scripts/check_turbo_cache_writer.py` exit0.

## Results

Six cases pass; all canaries intact. Five native outputs byte-identical to
reverse-mapped CPU encodings. Layer31/Turbo4 differs by one byte in one half
norm (CPU142/Metal141); all packed centroid codes identical. Independent byte
classification audit records this. Rotated reconstruction relative L2
3.1495e-5 there, zero in remaining cases. Peak pressure1/swap growth0.

## Evidence and disposition

`evidence/AW-0117-native-cache-writer.json`; raw evidence
`/Users/chad/Models/agentwing/evidence/AW-0117`. Retain native Turbo value
writers for integration with validated attention/inverse components. No q8 K
writer check, whole update/attention/inverse graph, Prism registration/allocation,
accumulated compressed generation, long-context/vision/model quality or endpoint
claim. P1/current FP16 runtime unchanged.
