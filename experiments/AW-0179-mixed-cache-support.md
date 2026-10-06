# AW-0179 — isolated mixed-cache native support

Prepared, unbuilt/untested; unresolved, no promotion. AW178 reveals native
support gates prevent matched K/V isolation. Hypothesis: instantiate existing
independent half/Q8/Turbo4 dequantizers for256x256 heads, permitting Metal
q8K/F16V and F16K/Turbo4V without altered quantizers/sampling/model behavior.
Four-file isolated patch atop AW137/baseadfffbe, original runtime untouched.

New block/vector mixed kernels, narrowed device admission and execution assert;
context permits F16K only with Turbo4V, not Turbo3. Mixed-format inputs bypass
same-type F16scratch path because it reuses K's pipeline to dequantize V.
Scratch sizing accounts for either quantized side. No model downloads/data
changes. Same-type and original q8/Turbo profiles retained.

Required before use: native build, finite/oracle prefill and decode attention
for both mixes, selected backend/kernel authority, full16K host gates then
identical-prefix own32 replay. Full multimodal/tool/end-to-end gates still
required. No performance claim from prepared source. Avoid compiler/GPU work
alongside AW178's live diagnostic; build only after terminal state confirmed.

Patch: experiments/runtime-patches/AW-0179-mixed-cache.patch.
Pins/plan: evidence/AW-0179-mixed-cache-plan.json.
External source: /Users/chad/Models/agentwing/runtime-sources/prism-turbo-mixed.
External evidence: /Users/chad/Models/agentwing/evidence/AW-0179.
P1/default/deployed runtimes unchanged.

## Native build result

Pinned CMake3.31.6/Ninja explicit paths, Release/embeddedMetal/OpenSSLoff;
llama and ggml-metal targets269steps -j4 completed exit0. Compared3531 source
files against AW137 port: only declared fourfiles differ. All generated dylib
hashes recorded. Archive-derived source has noGit version identity; pinned
base/patch/source hashes are authority. This C++ build embeds Metal source,
not proof of runtime shader compilation or numerical correctness. Next run
real early/middle/late attention decode/prefill canaries against independently
dequantized CPU oracle before full-model replay. No acceptance/promotion.
Receipt: evidence/AW-0179-mixed-cache-build.json.
