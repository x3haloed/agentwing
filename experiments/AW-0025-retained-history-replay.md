# AW-0025 — Retain exact spelling for older tool turns

## Status

Source diagnosis recorded; no runtime change or endpoint remedy measured.

## Observation

AW-0019 full-suite task 05 passed in 656 task seconds, but its final request
reprocessed 1,076 prompt tokens with zero KV reuse and 868 prefix tokens matched.
Time to first token was 283.8 seconds. This occurred despite a tool-replay hit.
Tasks 01–04 had no zero-reuse continuations in their completed metric logs.
See `evidence/AW-0019-provisional-prefix-refills.json`.

## Source mechanism and hypothesis

Pinned Swiftlet `459b201` stores only one `signatures` array and one `rawText`
in `ToolReplayCache` (`Sources/SwiftletServer/ToolProtocol.swift`). Each `record`
replaces the previous entry. When every assistant message is converted during
the next request, only the newest tool turn can recover its exact raw spelling;
older turns fall back to structured serialization. If an older turn's raw
spelling differs from canonical serialization, a later prompt can diverge
inside its already-consumed history and safely trigger a full refill.

This source behavior supports the observed mechanism, but the exact divergent
bytes in the real run were not captured. A tool-replay hit measures a raw-text
lookup, not a successful KV-prefix match. Do not equate the two counters.

## Bounded remedy to test if warranted

Retain exact raw replies for the tool turns still echoed in the current
conversation, under explicit entry and byte limits. Preserve strict matching
of IDs, type, name, and canonical arguments; mismatches must use the safe
structured path. Prune records no longer present in incoming history, clear
on a fresh conversation, and use bounded eviction with safe refill fallback.
Do not introduce lossy history rewriting or unbounded cross-task retention.

## Cheap falsifier

Before changing the runtime, write a three-turn fixture where the first call
has noncanonical whitespace and a second call is recorded. Demonstrate that
the third prompt loses the first call's raw spelling under the current cache.
Then require both earlier and latest exact spellings, unchanged mismatch
rejection, fresh-task clearing, eviction boundaries, and existing protocol and
prefix-state tests. Rebuild only after the live suite terminates.

## Endpoint acceptance and disposition

If selected after full-suite profiling, compare the same data task and require
preserved utility with removal of the observed continuation refill. Count all
costs, failures, and memory growth. Replicated full-suite gates still govern
promotion. This remains an unimplemented option; the current screen is unchanged.
