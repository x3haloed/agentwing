# AW-0129 — Corrected asymmetric attention specialization placement

Retained build stage. Correct AW-0127 vector-specialization placement so macros
remain defined; arithmetic/accepted type pairs/configuration otherwise unchanged.
Frozen full patch `experiments/runtime-patches/AW-0129-turbo-attention.patch`
applies cleanly to Prismadfffbe baseline. Original and failed build artifacts
preserved; new output directory `/Users/chad/Models/agentwing/runtime-builds/prism-turbo-attention-fixed`.

External plan pins source/patch/harness/compiler/tool/host and argv. Same build
rule CMake/Ninja Release embedded Metal,targetllama,parallel2,600s/phase timeout,
.5s host checks. `python3 scripts/build_prism_turbo_attention_fixed.py` exit0.
Configure3.082s/build71.003s,pressure1/swap growth0; no performance claim.
No new model inference/task/tool/permission/sampling changes. Exact source
Prismadfffbe/Atomic074bf826, MIT; internal SSD M1/16GB/macOS27.0.1.

Evidence `evidence/AW-0129-prism-attention.json`; raw
`/Users/chad/Models/agentwing/evidence/AW-0129`. Runtime compilation and graph
accuracy validated separately AW-0130. Retain stage, no endpoint admission;
AW-0128 negative result intact.
