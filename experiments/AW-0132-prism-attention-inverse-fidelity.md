# AW-0132 — Prism attention and inverse graph fidelity

Retained. Hypothesis: integrated asymmetric attention→inverse graph reproduces
independent compressed CPU output at real layers3/31/63 for Turbo3/4, with
explicit unsupported CPU inverse denial.

Plan freezes new build AW-0131/runtime dylibs, native probe/harness/binary,
input AW-0116 and independent CPU AW-0113 authority. Probe invokes actual
Prism ggml_flash_attn_ext followed by ggml_turbo_inverse; both Metal support
checks must pass and CPU support check must be false. Whole graph computed
through backend, no direct Swift dispatch/CPU intermediate reconstruction.
Actual24 Q/fourKV heads,256 dimensions,48 populated/64 padded cache positions,
scale.0625, no bias/softcap/sinks, F16 padded mask64×32. Captured trajectory
AW-0109 uses FP16 cache; no new model inference/sampler/task/tool/permission change.
Fixed internal SSD M1/16GB/macOS27.0.1.

Primary rule six supported/exit0 full finite6144 outputs, relative L2<=.005
versus independent CPU inverse of AW-0113 rotated compressed aggregate, CPU
inverse graph denied.90s/case watchdog/.25s host checks.
`python3 scripts/check_prism_turbo_attention_inverse.py` exit0; all six pass.
Errors Turbo3 layers3/31/63 .00068293/.00125468/.00065262; Turbo4
.00068023/.00129833/.00068892. These final files byte-identical to AW-0119
standalone native chain outputs. Pressure1/swap growth0.

Evidence `evidence/AW-0132-prism-inverse.json`, raw
`/Users/chad/Models/agentwing/evidence/AW-0132`. Retain backend graph stage.
Model-cache graph/actual allocations, prefill, compressed accumulated generation,
vision and endpoint performance remain unverified; no qualification/P1 change.
