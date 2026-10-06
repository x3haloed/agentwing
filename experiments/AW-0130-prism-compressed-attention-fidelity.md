# AW-0130 — Integrated Prism compressed attention fidelity

## Status and hypothesis

Retained. Corrected Prism backend can initialize split Metal libraries and
execute actual ggml_flash_attn_ext q8-K/Turbo3/4-V256/256 graph, agreeing with
independent compressed CPU attention at actual layers3/31/63.

## Frozen configuration and acceptance

Plan pins AW-0129 build authority, every dylib, native probe/harness/binary,
AW-0116 real input authority and AW-0113 compressed CPU authority. Native Prism
tensor allocation/support check/graph execution APIs are used; no direct Swift
dispatch. F32 Q shape256×1×24×1; K/V256×64×4×1,48 active/16 zero padded positions;
F16 mask64×32 supplies frontend-required padding but only first query is used.
Scale.0625, no sinks/bias/softcap. Output6144 F32 values, rotated V basis.

Primary predeclared rule six graphs supported/exit0,all finite and relative L2
<=.005 versus independent CPU rotated aggregates.90s/case watchdog,.25s host
checks. Same actual captured trajectory AW-0109, sampling/model/runtime lineage
preserved; no new model inference/task/verifier/tools/permission changes.
Fixed internal SSD M1/16GB/macOS27.0.1. Turbo mixed-format path forces available
baseline vector specialization and disables invalid same-format dequant shortcut.

`python3 scripts/check_prism_turbo_attention_fixed.py` exit0.

## Results

| Layer | Turbo3 relative L2 | Turbo4 relative L2 |
| --- | ---: | ---: |
| 3 | .00029880 | .00025532 |
| 31 | .00101193 | .00112943 |
| 63 | .00020252 | .00017833 |

All six complete graphs/output arrays pass. Native logs confirm actual
specialized pipeline selection/compiled libraries. Pressure1/swap growth0.
Build-only false confidence is falsified by preserved AW-0128 initialization
failure; corrected runtime is independently checked, not inferred from build.

## Evidence and limits

`evidence/AW-0130-prism-attention.json`; raw
`/Users/chad/Models/agentwing/evidence/AW-0130`. Retain backend attention stage.
This is decode graph coverage; non-vector/prefill declarations compile but
prefill execution/fidelity remains untested. Inverse op/model cache graph,
actual compressed allocation, accumulated compressed generation, vision and
endpoint comparisons remain outstanding. P1/default runtime unchanged.
