# AW-0186 — isolated stationary4-bit CPU/Metal tables

Hypothesis: AW185 same-layout survivor can be installed with coordinated table
literal changes only. New isolated source/build inherits AW137/AW179/AW182
baseadfffbe. Exactly two inherited sourcefiles change: ggml-turbo-quant.c and
Metal dequantize.h. Float/half/magnitude centroid tables and decision cuts change
together. Nine-significant-digit roundtripF32 values, zero midpoint retained;
no layout/rotation/normcorrection/kernel/quantizer algorithm changes. Old cache
bytes require old runtime, so no existing persistent cache/profile is migrated.

Native Release/embeddedMetal/OpenSSLoff pinned CMake/Ninja llama+ggml-metal
269steps -j4 exit0. Compared3531 inherited sourcefiles, only declaredtwo differ;
all generated library/config/source/patch hashes recorded. CPU native encoder
packedbytes and decoder vectors bitexact AW185 candidate across384blocks in
eachlayer3/31/63,1152total. This proves CPU table installation on captured inputs,
not Metal runtime compilation or kernel cost/model behavior.

Retain build/integrity survivor. Next GPU reverse-index writer and block/vector
attention numeric and complete cost screens before expensive own accumulated
model replay, native tools/vision and replicated endpoint acceptance. No speed /
quality promotion, model/task/sampling/default/P1/deployedruntime changes.
Full patch series and AW185 source/modelcapture/codebook authority in plan.
No model loaded or performance claim from this build/CPU parity test.

Raw: /Users/chad/Models/agentwing/evidence/AW-0186.
Source/build external suffix prism-turbo-codebook. Reproduce configure/build
logs, then native quantize/dequantize/inverse CPU parity against AW185 fixtures.
Manifest: evidence/AW-0186-stationary-codebook-build.json.
Patch: experiments/runtime-patches/AW-0186-stationary-codebook.patch.
Disposition retained for GPU screening, unqualified for deployment.
