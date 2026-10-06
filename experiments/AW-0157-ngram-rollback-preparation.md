# AW-0157 — bounded ngram rollback preparation

Hypothesis: three bounded rollback slots are a plausible memory candidate and
allocation can be enabled for ngram-simple while preserving existing methods.
Primary metric: source-derived tensor scaling and compiled allocation canaries.
No inference, whole-process safety or speed claim.

Source allocates recurrent tensors with mem_size*(1+n_rs_seq) rows. AW151's
rounded149.62MiB thus estimates598.48MiB for3slots, an added448.86MiB.
At16K, q8K/Turbo4V408MiB plus estimated RS598.48 totals1006.48MiB versus
F16KV1024 plus original RS149.62 totaling1173.62MiB. This excludes weights,
vision, graph, allocator and other host memory. It is only a fit hypothesis.
Microbatch must be at least5 or existing fallback disables3slots.

Prepare incremental common.h patch to return max(existing draft requirement,
ngram-simple proposal size). Do not apply it to the current port or change
frozen binaries/profiles. Extracted patched method compiles with lightweight
mock fields/enums: no-spec0, ngram3, draft7, mixed max7/max9 all pass. This tests
allocation selection only, not rollback semantics or full-server integration.

Proposed first candidate lookup2/proposal3 fits the current4-column PTQ path;
AW156 oracle opportunity1.343461 excludes actual costs and is not performance.
All native medium thinking, context, tool/task/verifier and permissions remain
unchanged; no reasoning budget reduction. Model/runtime/harness/host provenance
inherits AW141/AW148/AW151, parent source and profile hashes pinned in receipt.

Retain for isolated new runtime build, measured memory admission and forced
rejection fidelity tests before actual complete-cost and endpoint evaluation.
No promotion, P1 frozen. Patch: experiments/runtime-patches/AW-0157-ngram-rollback.patch.
Receipt: evidence/AW-0157-ngram-rollback-preparation.json.
External canary/source/plan/binary/compiler hashes:
/Users/chad/Models/agentwing/evidence/AW-0157.
