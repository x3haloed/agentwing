# AW-0127 — Initial asymmetric attention build

Rejected integration revision after AW-0128 runtime falsifier. Hypothesis:
Prism split Metal library can add q8-K/Turbo3/4-V256/256 attention without
replacing existing weight kernels. Remapped base/writer stage AW-0125 extended
with unchanged Atomic dequantizers and vector/non-vector specializations.
Shared helpers move from quantize kernel into dequantize header. Support and
pipeline-name routing allow only proven q8-K/Turbo3/4-V256/256 pairs. Disable
same-format KV-to-F16 shortcut for mixed formats; choose available baseline
vector specialization for Turbo rather than unrelated q8 tuning entries.

Frozen full patch/source/command/tool/compiler/host pins in external plan.
CMake/Ninja Release embedded Metal targetllama/parallel2 configure/build pass
(exit0;3.085s/71.029s), pressure1/swap growth0. Build-only rule satisfied, but
shaders compile at runtime: AW-0128 rejects macro placement. Preserve patch
`experiments/runtime-patches/AW-0127-rejected-turbo-attention.patch` and raw
`/Users/chad/Models/agentwing/evidence/AW-0127`; metadata
`evidence/AW-0127-prism-attention.json`. No compressed model generation or
endpoint claim. P1/default launcher untouched.
