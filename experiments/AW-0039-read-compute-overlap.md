# AW-0039 — Causal read/compute submission screen

Hypothesis: submitting original expert computations as their reads become ready
preserves every stage output and can overlap I/O without changing routing.
Before runtime integration, compare original fast8 gate/up/SwiGLU/down for the
72 AW-0036 real fixtures against AW-0037 hashes. Require all 576 expert outputs
bit-identical in every arm; any discrepancy prevents continuation.

Five interleaved arms C/A/C/A/C use eight shared weight buffers. Both launch all
eight preads concurrently. C waits for all reads, then submits one command buffer;
A waits for each expert in routed order and submits its command buffer while
later reads can still run. Retain all buffers until every command completes.
No future-layer routing knowledge or quantization; no altered mixture ordering.
The control is a diagnostic schedule, not the complete P1 MoE encoder.

Record read-plus-encode-plus-GPU-completion wall time, excluding fixture setup and
hashing. Report submission overhead and process block-input counters. These small
three-layer fixtures can fit the OS cache; do not infer SSD savings, production
cache behavior, full-model parity or autonomous utility from this screen. Shared
expert work, cache policy and chunked-prefill batching remain integration costs.
AW-0037 wrapper provenance, source/layout pins, lock, 300-second timeout, pressure
and swap gates apply. Large evidence stays outside Git. P1 remains frozen.

## Result — retained for runtime investigation

All 2,880 expert executions (576 per arm) match AW-0037 stage SHA256 values
exactly, including gate, up, SwiGLU and down outputs. Both raw receipts and
fixture identity were audited by `scripts/audit_expert_overlap.py`.

C/A/C/A/C measured 0.362274 / 0.327641 / 0.370233 / 0.323074 / 0.355488 seconds.
Candidate wall ratios to neighboring-control means are 0.894574 and 0.890353.
Every process input-block delta is zero. Thus this clears a cached-path overhead
screen only; it does not demonstrate disk-read overlap, disk-byte reduction or
an agent speedup. The diagnostic control also sequences each expert's entire
projection chain, whereas P1 groups gate/up projections before down projections.
That scheduling difference is an additional limit on transferring timing results.

Raw run: `/Users/chad/Models/agentwing/evidence/AW-0039/20260906T065000.783222Z`.
Receipt SHA256: `546695393768759e6ea70837dee4efa238b25f07a4bcec51561b4fe3bac1e03b`.
Summary: `evidence/AW-0039-overlap-results.json`. Exit 0, pressure 1, zero swap
growth, and post-run P1 preflight passes. No full-model or held-out execution.
Retain the mechanism for an isolated runtime implementation with original LFU
selection, failed-read invalidation, cancellation cleanup, and unchanged final
accumulation. Measure all shared/chunk work and actual process disk activity in
interleaved model runs before deciding whether endpoint evaluation is warranted.
