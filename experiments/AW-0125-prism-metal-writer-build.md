# AW-0125 — Prism Metal cache-writer integration build

Retained. Hypothesis: append unchanged validated Atomic Turbo SET_ROWS helpers,
kernels and specializations to Prism's split quantize Metal library and enable
backend support without replacing Prism's existing weight kernels.

Complete frozen patch extends AW-0123 remapped types/CPU codecs; it adds actual
Atomic helpers/writers to kernels/quantize.metal and SET_ROWS type-support cases.
Existing Prism pipeline naming and argument/thread dispatch remain unchanged.
No attention/inverse/cache-graph changes. Sources: Prismadfffbe and
Atomic074bf826e1b06005a51737d29387e36657f41bf7, public MIT. Original source/build
baseline preserved, separate experimental source checkout. Frozen full patch
`experiments/runtime-patches/AW-0125-turbo-metal-writer.patch` applies cleanly to
original pinned Prism (`git apply --check`).

Plan pins patch/source/harness/compiler/tool/host and argv. CMake3.31.6/Ninja
1.11.1.4 Release embedded Metal,targetllama,parallel2. Output isolated at
`/Users/chad/Models/agentwing/runtime-builds/prism-turbo-metal-writer`.
Primary rule configure/build exits0,nonemptylibs,host gates;600s/phase timeout,
.5s host sampling. `python3 scripts/build_prism_turbo_metal_writer.py` exit0.
Configure3.591s/build70.984s,pressure1/swap growth0. These build diagnostics are
not performance claims. Fixed internal SSD M1/16GB/macOS27.0.1/26A434.

Evidence `evidence/AW-0125-prism-metal-writer.json`, raw
`/Users/chad/Models/agentwing/evidence/AW-0125`. No model inference/task/tool/
permission/sampling changes. Retain build for AW-0126 graph check; compile alone
cannot admit Metal runtime or model-cache operation. P1/current launcher intact.
