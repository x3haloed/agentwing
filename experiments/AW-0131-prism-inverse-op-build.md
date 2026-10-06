# AW-0131 — Prism inverse WHT operation build

Retained graph stage. Append GGML_OP_TURBO_INVERSE after existing operations,
COUNT101→102, preserving old IDs/names; public factory requires contiguous F32,
head dimension divisible128. Creates distinct output tensor and native Metal
operation dispatches unchanged validated Atomic inverse128-group WHT. Explicit
CPU backend supports-op denial prevents unsupported fallback. CPU direct codec
inverse remains independently validated; full CPU graph inverse not implemented.

Frozen full patch `experiments/runtime-patches/AW-0131-turbo-inverse.patch`
extends AW-0129, with exact source/harness/compiler/tool/host/argv pins in plan.
Separate isolated output `/Users/chad/Models/agentwing/runtime-builds/prism-turbo-inverse`.
Same Release embedded Metal targetllama/parallel2,600s/phase watchdog/.5s checks.
`python3 scripts/build_prism_turbo_inverse.py` exit0; configure3.591s/build71.032s,
pressure1/swap growth0. Compile warnings include unhandled new operation in
CPU forward switch; support explicitly declines it, no CPU graph claim.

Source Prismadfffbe and Atomic074bf826 public MIT, internal SSD M1/16GB/macOS
27.0.1/26A434. No model/task/tool/sampling/permission changes or performance claim.
Evidence `evidence/AW-0131-prism-inverse.json`; raw
`/Users/chad/Models/agentwing/evidence/AW-0131`. Actual combined graph checked
AW-0132. Header repeated-include defect subsequently corrected AW-0134 source;
this built binary preserved, not relabeled as corrected rebuilt artifact.
