# AW-0092 — Interleaved real projection packing cost screen

## Status and hypothesis

Complete diagnostic. Hypothesis: exact PQ can reduce complete graph-operation
cost despite larger weights. Before execution freeze ABBA repeated3 times for
each early/middle/late FFN-up tensor at1 and16 columns; retain all first ABBA
warmup timings, exclude only those four from steady diagnostic. Retain for
further whole-model screening only if median warm total PTQ/PQ>1 for at least
one tested operation. No promotion or endpoint acceptance rule.

## Results

Single-column total ratios PTQ/PQ:0.892/0.779/0.796 (PQ slower). Compute-only
ratios approximately0.949/0.775/0.738; repeated installation is not the only
source of loss. Sixteen-column totals1.095/1.083/1.096 (PQ modestly faster).
Both outputs finite throughout; pressure1/swap0; no thermal warnings recorded.
Preserve every trial and complete per-case process wall time. Native process
walls include backend setup; graph totals include metadata/backend allocation,
weight/input transfers, synchronous compute, readback and cleanup. Whole harness
hashing/verification overhead is not in graph/process diagnostic metrics.

## Complete-cost context and limitations

Each selected tensor grows19,496,960→23,674,880 bytes. Uniform full artifact
would grow1,259,520,000 bytes (1.173 GiB; AW-0079/AW-0083). This probe loads
both representations' host fixtures and only one arm's device graph at a time.
It does not measure full-model residency, OS cold I/O, streamed conversion,
whole installation peak, vision overhead or agent endpoint cost. A19–24MB
projection cache working set differs from the full6–7GB model. Recreating and
installing weights each graph differs from resident per-token execution;
compute-only timings are retained separately. Sparse family selection (FFN-up
only), few repetitions and uncontrolled page/shader cache limit extrapolation.
AW-0079 already bounds perfect prefill-only improvement to~3.7% on exposed
debugging, not a universal endpoint bound. No25% gain follows from this screen.

## Configuration and commands

Fixed16GB M1 Macmini9,1/internal SSD/macOS27.0.1 build26A434; Prism runtime
adfffbe41b2cabcd51fff326ab045662265062bb and model HF revision
b072e1d3b35a0a630cece372c2127528e0994386. Actual AW-0088 inputs, complete
AW-0086 FFN-up weights/exact repacking; same native pinned headers/dylibs.
No sampling, context, KV, tools, task scoring or permissions in isolated graph.
Native source compiled clang++ -std=c++17 -O2 with pinned header include,
links -lggml -lggml-base -lggml-metal and absolute rpath.
Executed python3 scripts/check_bonsai_packing_cost.py (exit0).
External /Users/chad/Models/agentwing/evidence/AW-0092 contains frozen plan,
all timings/logs/host samples/binary/result/recursive hashes. Small committed
evidence/AW-0092-packing-cost-screen.json carries exact result/source hashes.

## Disposition

Retained under the predeclared rule for other operation-family and resident
weight screening because16-column cases improve. Uniform full conversion is
not justified by this decode-heavy evidence; no model artifact changed. Frozen
P1, endpoint corpus and reasoning/timeout/permission/scoring remain unchanged.
