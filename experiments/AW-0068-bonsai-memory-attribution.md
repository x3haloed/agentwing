# AW-0068 — Full vision/text startup memory attribution

Retained component evidence, 2026-10-05; successor remains unqualified.

A fresh pinned full text/vision server, 8K FP16 KV, one slot and publisher
thinking sampling is started under existing host gates. Verbosity 5 exposes
allocation sizes. No task is scored and no model or vision capacity is removed.
Reproduce with `PYTHONDONTWRITEBYTECODE=1 python3 scripts/probe_bonsai_memory.py`.
Model, runtime, hardware, OS, command and raw hashes are recorded externally in
`/Users/chad/Models/agentwing/evidence/AW-0068/20261006T033033.678912Z`.
Small receipt/audit: `evidence/AW-0068-memory-attribution.json`.

Startup reaches health with pressure 1, zero swap growth, peak RSS 7,299,776 KiB.
KV is 512 MiB (256 K + 256 V), recurrent state 149.62 MiB. Vision compute reserve
is 248.10 MiB plus CPU 24.93 MiB; language compute is 75.71 plus CPU 7 MiB.
These reported buffers and RSS are different accounting views, not additive
physical ownership measurements. Weight payloads remain those audited by AW64.

RAM prompt-state cache defaults to an 8192 MiB ceiling. Pinned server source
serializes sequence state when replacing sufficiently dissimilar prompts or
using LRU selection. A ceiling is not allocated residency; AW66's low verbosity
cannot establish whether cached states caused its pressure failure. AW69 tests
one complete refactor with this optional archive cache disabled, full context
and supported thinking retained, with verbose logs. Changing sampler relative to
AW66 means this is not an isolated causal pair or speed comparison.

User requests TurboQuant/PolarCache if KV/model memory is material. Google's
primary sources call the constituent algorithm PolarQuant:
https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/
https://research.google/pubs/polarquant-quantizing-kv-caches-with-polar-transformation/
Pinned binary help advertises f32/f16/bf16/q8/q4/q5/iq4 KV types, no TurboQuant.
Conventional q4 does not implement its rotation and QJL correction. Retain
TurboQuant as an explicit integration candidate; first verify Qwen35 hybrid
state, Metal kernels, accumulated attention quality, installation and temporary
cost. At 8K, even eliminating the entire KV saves at most its 512 MiB allocation;
compression cannot reduce language/vision weights or recurrent state by itself.
No universal zero-loss or M1 speed claim follows from Google's tested models.
