# AW-0155 — history speculation checkpoint cost falsifier

## Status

Read-only screen complete; zero-cost rollback hypothesis rejected.

## Hypothesis and primary metric

Ngram3/3 can use bounded recurrent rollback in the unchanged pinned server.
Metric: source-path eligibility and required checkpoint/replay operations.
No inference, timing, endpoint or capability claim.

## Configuration identities and fixed conditions

Same source/profile as AW151, same model/native sampling and fourth-generation
history as AW141/AW154. Full model, runtime, harness, context16384, cache,
vision, native medium reasoning and host provenance remain in those receipts.
No model process launched, no tools executed, no task/verifier/default changes.
Runtime source hashes and parent receipt hash frozen before the static screen.

## Cheap falsifier and results

common_params_speculative::need_n_rs_seq includes draft-model methods but
excludes ngram methods: it returns0. AW151 measured0rs_seq and logged use of
checkpoints. server-context.cpp creates a partial-only checkpoint before every
nonempty draft. A rejected draft restores checkpoint and sampler, truncates
prompt state, marks spec_is_replay and returns for a further decode.

Applied conditionally to the exact AW154 oracle trajectory:1381 checkpoint
creations,1029 restores and at least1029 additional replay passes beyond6168
initial verification passes.7197 total versus7694 baseline gives an equal-cost
pass ratio1.069057, before copies, lookup, batching and possible further replay.
This is a static conditional cost count, not measured throughput, an endpoint
speedup, or a universal bound on a different execution kernel. Replay/fidelity
is not yet experimentally validated. Preserve AW154 count and qualify its
initial-pass-only interpretation rather than deleting it.

## Evidence and disposition

External plan and exact source excerpts:
/Users/chad/Models/agentwing/evidence/AW-0155.
Small hash receipt: evidence/AW-0155-history-checkpoint-cost.json.
Reject the unchanged path as presumed cheap acceleration. A new rolling-state
allocation candidate remains unresolved and must establish extra memory,
rollback fidelity, complete cost and endpoint gates. No promotion; P1 frozen.
