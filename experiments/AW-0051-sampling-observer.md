# AW-0051 — Observe the long tool-generation failure

## Status

Observer build and focused tests pass after terminal AW-0049/AW-0050. No real
model capture yet; diagnostic runner and capture audit remain to be prepared.

## Hypothesis

A read-only observer on the unchanged joint runtime can reproduce the fixed-path
multi-file failure while recording actual prompt/token history and greedy
sampling scores. The capture can then distinguish numerical anomalies and
penalty-driven selections from repetition already favored by raw model logits.
It does not presume that any of these explanations is correct.

## Configuration and primary metric

Create an isolated runtime from AW-0047 revision
4dff62e867d62288d4224974c4add523dad50437. Preserve P1 and AW-0047 sources/binaries.
Do not change model, sampler options, task, prompt, tools, permission boundary,
512-token output ceiling, deadlines, cache budget or grading. Keep the same
fixed live workspace path. Instrument only an opt-in observer.

Primary diagnostic: complete captured token decisions with reproduction of
AW-0049's structured visible trajectory and failure. If the trajectory differs,
retain the capture but do not claim observation is behavior-neutral for that
case. This is development-only and supplies no performance or promotion claim.

## Observer design and cheap falsifier

Record actual represented prompt token IDs, rendered prompt IDs, prefix reuse,
generation options and admitted output budget per request. For greedy decisions,
record selected token, prior occurrence count, raw and adjusted scores, bounded
top candidates, and nonfinite/range statistics. Record final generated IDs and
finish reason. Do not dump full logit tensors or change any selected token.
Keep traces outside Git and preserve their hashes.

First test serialization, nonfinite handling, bounded candidate selection,
no-overwrite output creation and observer-off behavior. Run existing focused
runtime tests before the single real development capture. Freeze source, binary,
kernel, runner and settings pins before model execution. Preserve failed tests
and incomplete captures. Do not infer physical I/O savings from observer timings.

## Stop rules and next decision

Use existing host and task deadlines and retain any protocol rejection. The
expected diagnostic failure is not repaired, scored as success, or followed by
held-out work. Audit the trace and source identity before selecting a subsequent
falsifier or runtime change. The earlier source review found that generated
counts are local to each request and increment after selection; it did not
establish a counter bug or prove the rest of sampling correct.

## Disposition

Unresolved. This diagnostic is preparation for a capability repair, not a new
acceptance criterion or a completed project goal.

## Build validation

Isolated runtime revision `e781ebeb6c77101dbf845419c5ece099d1d1e4d2`, tree
`8f2921d1df248714b275ef5055aa009c3dfeb31a`. The archived patch reconstructs that
exact tree from AW-0047's pinned source. P1 and the original candidate remain
unchanged. Release SwiftPM build used two jobs with dependency resolution disabled;
only dependency sources were copied into the isolated build directory.

All 53 selected tests across eight suites pass, including trace nonfinite/ranking
serialization, exclusive output creation, and identical model-step sequences
and emitted text with observation on/off in the injected-model session test.
The remaining focused tests cover existing context, lifecycle, stop and repetition
behavior. This does not establish real-model neutrality or explain the failure.
P1 preflight passes afterward; no model process remains live.

Evidence: `evidence/AW-0051-observer-build-tests.json`;
isolated profile: `spec/sampling-observer-development.json`;
reconstruction: `experiments/AW-0051-sampling-observer.patch`.
