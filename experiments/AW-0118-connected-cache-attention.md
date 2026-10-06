# AW-0118 — Connected native cache writer, attention and inverse

## Status and hypothesis

Retained. Unchanged Atomic GPU Turbo3/4 value writer, compressed attention and
inverse WHT compose without CPU reconstruction or transfer between stages and
agree with independent compressed CPU attention authority on actual Bonsai
layers3/31/63 within predeclared relative L2 .005.

## Configuration and execution

Frozen external plan pins runner/harness/binary, complete Atomic Metal source,
AW-0109 capture, AW-0113 CPU authority and every input/index/argument byte.
Model/runtime/sampling/context provenance inherits AW-0109 FP16-generated
trajectory; no new model inference, task/verifier/tools/permission changes.
Internal SSD, M1 Macmini9,1/16GB/macOS27.0.1/26A434. Native Metal3.0.

24 Q/four KV heads,256 dimensions,48 populated positions. Value writer maps
192 source rows into four64-row cache regions, leaving16 slots per head zero;
mask excludes them with-inf. Key cache is CPU q8 prepared as AW-0116.
One command buffer per case contains separate ordered compute encoders for
SET_ROWS, compressed attention and inverse WHT. Cache/output remain shared GPU
buffers; no CPU readback/reconstruction between stages. No kernel arithmetic
changes. Attention constants/dispatch/scratch inherit AW-0116; writer ABI
inherits AW-0117, now indexed head*64+token. Inverse48groups uses64threads.

`python3 scripts/check_turbo_cache_attention_chain.py` exit0.90s watchdog and
.25s host checks, pressure peak1/swap growth0. Complete final output finite;
primary rule relative L2<=.005 versus CPU inverse of AW-0113 compressed rotated
aggregate, six cases. Transform/composition acceptance only, not model quality.

## Results

| Layer | Turbo3 relative L2 | Turbo4 relative L2 |
| --- | ---: | ---: |
| 3 | .00068293 | .00068023 |
| 31 | .00125468 | .00129833 |
| 63 | .00065262 | .00068892 |

All six6144-value outputs pass. Independent cache audit proves all192 populated
writer rows exactly match AW-0117 native output at corresponding indices; all
masked padding zero. No endpoint/throughput or full-installation cost claim.

## Evidence and disposition

`evidence/AW-0118-connected-cache-attention.json`; external raw evidence
`/Users/chad/Models/agentwing/evidence/AW-0118`.
Retain connected value-side execution path for integration. q8 K remains CPU
prepared; Prism type registration/cache graph, actual compressed allocation,
accumulated compressed model generation, longer contexts, vision and independent
endpoint qualification remain outstanding. P1/current FP16 runtime unchanged.
