# AW-0037 — Original fast8 routed expert numerical reference

Hypothesis: a bounded standalone harness executing P1's unmodified Metal kernels
on AW-0036 real inputs agrees with independent double-precision affine projection
and SwiGLU checks, providing references for candidate recoding. Primary gate:
relative L2 <=1e-4 for each original projection, activation and routed mixture.
This is an implementation-integrity screen, not a candidate fidelity threshold.

Use the exact P1 kernel source and default Metal compilation options. Read original
qpack expert blobs, group size 64, U8 weights, BF16 scales/biases. Check every gate,
up and down row with independent scalar double dequantization/accumulation; down
checks consume actual GPU SwiGLU inputs to isolate projection semantics. Check
SwiGLU against double exp on original GPU gate/up outputs. Execute the original
weighted_accum kernel with zero shared-expert/residual contribution to isolate the
routed mixture. Compare against double weighted sum of actual expert outputs.

All 72 captured activations / 576 selected experts, layers 0/20/39. Stage outputs
and mixture outputs are stored as raw F32 externally with source/output hashes.
One reusable expert buffer, no bank conversion or model loading. Sequential reads;
300-second deadline, pressure <4, swap growth <=1GiB, no concurrent model owner.
No performance inference from these reference timings. A failure stops fixture
admission and is preserved. P1, held-out tasks and frozen contracts unchanged.

## Results

First build at external `AW-0037/20260906T063206.816644Z` failed because the local
identifier I collided with the system complex-number macro. The source and compiler
log are preserved; renaming it interWidth resolved the build. No numerical run
occurred from that failed build.

Successful run: `/Users/chad/Models/agentwing/evidence/AW-0037/20260906T063224.469387Z`.
All 72 fixtures / 576 expert executions pass the predeclared 1e-4 integrity screen.
Maximum relative L2: projections 7.415531443e-6; SwiGLU 1.201760025e-7; routed
mixture 7.625419725e-8. The independent calculation intentionally has different
precision/reduction arithmetic; this is numerical agreement, not bit identity.

All raw hashes, output sizes, finite stage values and fixture/expert alignment
pass. Repeated layer/expert source hashes agree across fixtures. Raw F32 stage
files contain gate[512], up[512], SwiGLU[512], down[2048]; mixture files contain
2048 F32 values. Shared expert and residual contributions are zeroed only in the
standalone routed-mixture reference, never in P1's inference runtime.
Receipt SHA256: `fbc63d32717ae642bd97c5f319120c148cd95573fff002829ca54c4a208a44a4`.
Compact results: `evidence/AW-0037-original-reference-results.json`.

Execution took 5.03 seconds with pressure 1 and zero sampled swap growth; timings
include CPU reference work and are not representative inference or throughput
measurements. P1 preflight passes after cleanup. Disposition: original numerical
stage references admitted for candidate screening. No smaller representation,
candidate-accumulated trajectory or agentic gain has yet passed.
