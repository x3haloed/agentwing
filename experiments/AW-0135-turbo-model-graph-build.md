# AW-0135 — Wire compressed cache inverse into model graph

Retained integration build. Hypothesis: validated q8-K/Turbo3/4-V attention plus
inverse can be connected after native flash attention in Bonsai model graph,
without changing weight kernels, sampling policy or P1/control runtime.

Patch extends AW-0134 guarded operation with model graph wiring after attention
precision setup: Turbo3/4 V requires q8 K, contiguous output (explicit cont if
needed), then inverse operation and callback. Other cache types unchanged.
No symmetric Turbo K support claim. Native context must explicitly enable flash
attention; quantized V policy is enforced by existing runtime checks.

Frozen full patch `experiments/runtime-patches/AW-0135-turbo-model-graph.patch`
applies cleanly to exact Prismadfffbe source baseline; Atomic074bf826 MIT source
lineage preserved. Plan pins patch/source/harness/compiler/tool/host/argv.
Rebuild corrected header source and model graph into isolated
`/Users/chad/Models/agentwing/runtime-builds/prism-turbo-model`.
CMake/Ninja Release embedded Metal,targetllama/parallel2,600s/phase,.5s checks.
`python3 scripts/build_prism_turbo_model.py` exit0; configure3.077s/build71.004s,
pressure1/swap growth0. No runtime quality/performance claim from build times.

Evidence `evidence/AW-0135-turbo-model.json`; raw
`/Users/chad/Models/agentwing/evidence/AW-0135`. Fixed internal SSD M1/16GB/macOS
27.0.1, no model/task/tool/permission/sampling change during build. Actual model
execution separately AW-0136; P1/default launcher preserved.
