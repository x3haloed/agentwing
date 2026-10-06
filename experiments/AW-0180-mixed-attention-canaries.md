# AW-0180 — native mixed-cache attention integrity

## Hypothesis and fixed conditions

AW179 mixed kernels implement q8K/F16V and F16K/Turbo4V correctly, without CPU
fallback. Captured real own32 accumulated attention at layers3/31/63 from AW109;
48 active keys padded64, GQA24query/4KV heads, headwidth256. Existing packed
q8K/Turbo4V from AW116, original captured half K/V for uncompressed side.
One-query decode plus128replicated query columns to exercise block prefill
kernel; not a new real128-token prompt, causal-context or whole-cache test.
CPU independent float64 scores/softmax/value aggregation on explicitly decoded
packed formats; TurboV inverse WHT included. Same model/runtime/capture lineage
pinned in build/capture authorities; no new model/harness/tool/sampler run.

## Predeclared gate and result

All12 native graphs report supported, exit0, finite complete output relativeL2
<=.005. Observed maximum.001056661. Block and vector mixed pipeline names
explicitly selected; Metal runtime compilation succeeds. Independent raw/input /
source/library hashes, numerical ratios, host logs and kernel selections replay
valid. Wrong-KV-head mapping canary fails threshold all12. Pressure1, swapgrowth0,
baseline1119.12MiB. Initial compile18.621s retained; no performance comparison.
Fresh process per case, internalSSD, uncontrolled warm OS cache, hardware/OS /
thermal/compiler/library/source/input pins in plan. One owner,90s watchdog.

## Disposition and evidence

Retain component-integrity survivor only. Full16K allocations/own accumulated
model trajectories, tools/vision and replicated endpoint comparisons remain
required. P1/default/deployed runtime untouched. No Google full-algorithm claim.
Raw: /Users/chad/Models/agentwing/evidence/AW-0180.
Manifest: evidence/AW-0180-mixed-attention-canaries.json.
Fixture: experiments/fixtures/bonsai-mixed-attention.cpp compiled against AW179
libraries; python3 scripts/check_bonsai_mixed_attention.py. Refuses overwrite of
external directory; preserve original traces/oracles. Disposition retained.
