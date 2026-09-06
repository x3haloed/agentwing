# AW-0042 — Longer accumulated trajectories and route coverage

Test AW-0041's combined overlap on two new development prompts (Rust queue
design and multilingual record normalization), 64 generated tokens each.
No capability-panel tasks or held-out authorities are used. Compare C/A/C with
both overlap flags off/on/off and the same activation observer enabled in all.
Capture exact xmoe inputs and routing weights at layers 0/20/39, single-token
ordinals 0/7/15/31/47/63, and chunk-prefill ordinals 0/15/31/63 where present.
At most 30 records per arm. Require the final single-token ordinal 63 at all
three layers, and bit-identical corresponding records, full text, route sequence,
and cache decisions. Unexpected divergence blocks candidate continuation pending
diagnosis; an early EOS means this run has insufficient long-horizon coverage.

Measure newly exercised (layer, expert) identities relative to AW-0036's 250
admitted identities and uncommon identities (at most two selections) relative to
the fixed AW-0031 trace. These are explicit historical coverage measures, not a
claim of production rarity or exhaustive generalization.

Isolated `Swiftlet-AW0042` descends from AW-0041 d44752e. Capture is reconstructed
by `scripts/prepare_accumulated_capture.py`, retaining the already-admitted
observer's read-only input access but selecting later ordinals. Same 0.5 GB LFU,
sampling and runtime as prior diagnostics; only generated length and prompts
change. Record raw sources, binaries, hashes, full wall and process disk samples.
Common observer overhead makes timing diagnostic; P1 and all frozen evaluation
inputs remain unchanged. Pressure/swap gates, one model owner, lock and bounded
timeout apply. Passing permits further endpoint preparation, not promotion.

## Result — accumulated checks pass; longer-run speed benefit is smaller

Observer revision `f0ae501b4658a138cb77dd7cdd4e34947c70db80` builds, and its
patch reconstructs the recorded source tree. Initial setup omitted the required
checkout argument, so the first build was unchanged AW-0041; the observer was
subsequently applied and rebuilt before measurement. Provenance is recorded in
`evidence/AW-0042-build.json`.

Raw run: `/Users/chad/Models/agentwing/evidence/AW-0042/20260906T071526.059885Z`.
Receipt SHA256: `052962f239fde378f69dac1daa661a7816ebbb6e0a7e9c40ad9e3767b8933b08`.
All six arms reached 64 generated-token steps. Corresponding captured inputs and
weights match bit-for-bit, including ordinal 63 at all three layers: 27 records
per Rust arm, 30 per Unicode arm, 171 records total. Complete output text, routes
and LFU decisions also match within both C/A/C groups. Pressure stays 1, swap
growth 0, and post-run P1 preflight passes.

Rust exercises 5,186 distinct full-route identities, including 2,245 absent from
AW-0031. Its captured checkpoints include 55 identities beyond AW-0036 fixtures,
32 absent from AW-0031, and 59 seen only once/twice there. Unicode exercises
5,096 identities, including 2,239 absent from AW-0031; captured counts are 67
beyond AW-0036, 50 absent from AW-0031, and 55 seen once/twice. These measures
overlap and are case-specific, not additive population counts or production
rarity estimates. They extend historical coverage rather than prove universality.

| Case | Full process wall ratio | Prefill ratio | Decode ratio |
| --- | ---: | ---: | ---: |
| Rust queue | 0.8907 | 0.9109 | 0.8459 |
| Unicode records | 0.8948 | 0.9264 | 0.8489 |

Ratios use the mean of neighboring controls. Full wall is 46.275/41.241/46.326
seconds for Rust and 47.722/42.656/47.615 for Unicode. The approximately 1.12x
full-process speedup is materially smaller than AW-0041's short-prompt results.
Do not extrapolate the optimistic short-run effect to the 1.25x utility goal.
Retain the exact execution mechanism and accumulated evidence; further cost
reduction is needed before expensive promotion comparisons are justified.
One reachable next screen is overlapping the complete chunk expert chain using
an indexed activation batch, while charging extra dispatch/command overhead and
preserving each expert's token batching. Representation changes remain open.

Audit: `scripts/audit_accumulated_overlap.py`; summary:
`evidence/AW-0042-accumulated-results.json`. No held-out or agent task was run.
