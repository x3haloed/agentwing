# AW-0040 — Isolated single-token runtime overlap

Hypothesis: causal expert read/compute overlap reduces full-model decode wall
time while preserving routing and generated behavior. First integrate the
single-token path; chunked prefill retains its original implementation and all
its time remains charged. No task, tool, context or reasoning restriction.

Isolated checkout `Swiftlet-AW0040` descends from AW-0031 `406f992`.
`scripts/prepare_expert_overlap.py` reconstructs the source change. Original P1
is untouched. `SWIFTLET_EXPERT_OVERLAP=1` opts in; the same binary with it absent
is the instrumented control. LFU batch selection, allocated-byte cap and failed
fill invalidation remain. Distinct slot reads run concurrently; callbacks encode
only completed data on the caller thread. All reads and committed commands drain
before returning or throwing. Shared expert and ordered accumulation stay in the
original pending-MoE encoder, which skips already-computed routed projections.

Before model timing, verify cache hit/miss/eviction and readiness bytes, partial
read failures, and cancellation handling. Then interleave control/candidate runs
with the AW-0036 three development prompts and compare complete routes and text.
Reject any unexpected divergence pending diagnosis. Record process disk bytes,
full wall, reported prefill/decode time, pressure and swap. Per-phase counters
inside the new path are not yet comparable; no phase attribution claims.

No bank conversion, held-out task run or promotion. A performance survivor still
needs uncommon routes, longer accumulated behavior and replicated full agent
evaluation. Timing improvement in this experiment cannot satisfy the utility goal.

## Result — retained, not promoted

Runtime revision `234028121de5fe4d082b3198105466ff34f36cb6` builds in release
mode. The archived patch reconstructs its source tree from AW-0031. Eleven
focused tests pass across three suites, including ready-buffer contents through
hits/evictions, partial-read invalidation, cancellation after submission and fresh
state recovery with bit-identical tiny-model logits. The first request-stream
test accidentally generated no hits; its assertion caught this and the fixture
was corrected. A subsequent test command used the wrong working directory. Both
failures are preserved. `evidence/AW-0040-build-and-tests.json` pins logs and source.
The new async reader retains Sendable capture compiler warnings; distinct pointer
destinations and the locked error array have scoped lifetimes drained on return.

Raw run: `/Users/chad/Models/agentwing/evidence/AW-0040/20260906T065905.258759Z`.
Receipt SHA256: `eb7ca59de140b3d8b9f3777faea4820fb665037b2ea5fef14bb3a562ae39548b`.
Nine control/candidate/control model runs complete. Within each of coding,
arithmetic and structured cases, all output text, full route sequences, fetch
requests and miss decisions match. All pressure readings are 1, swap growth 0,
post-run P1 preflight passes. Sampled footprint stays approximately 2.62 GiB.

Candidate ratios to neighboring-control mean time:

| Case | Full process wall | Prefill | Decode |
| --- | ---: | ---: | ---: |
| Coding | 0.8474 | 0.9830 | 0.8854 |
| Arithmetic | 0.9825 | 1.0182 | 0.8880 |
| Structured | 0.8304 | 0.9741 | 0.8038 |

Unlike AW-0039, every arm has substantial observed process disk traffic
(12.53–16.86 GiB). Logical expert bytes are exactly equal within each case.
Thus the mechanism hides some execution/read latency; it removes no source
bytes, adds no codec/installation pass, and retains P1's cache and scratch sizes.
Extra command buffers and concurrent reads share unified-memory bandwidth.
Observed process disk bytes differ between arms, and startup/cache-state effects
contribute to full-wall differences. Do not assign the entire improvement to
SSD overlap or extrapolate these short runs to autonomous utility.

`scripts/audit_runtime_overlap.py` verifies receipts and comparisons;
`evidence/AW-0040-runtime-overlap-results.json` preserves numerical summaries.
Retain for further execution investigation. Chunked-prefill overlap, longer and
uncommon trajectories, complete phase instrumentation, and endpoint evaluation
remain unresolved. These results do not meet the active promotion goal.
