# AW-0045 — Investigate disappearing historical tool spellings

Status: source investigation and test authored; not executed. Do not build or run
this experiment concurrently with the fixed AW-0044 model comparison.

C1's final request matched 2237 prefix tokens but reused zero and re-prefilled
2425 tokens (654.1 seconds TTFT). P1 `ToolReplayCache` stores one signature array
and one raw reply string. `record` replaces both after every tool reply, so the
next request can replay only its newest assistant call. Older calls fall back to
structured template rendering. `SwiftletSession` only reuses state if the entire
cached token stream remains a prefix; a partial match triggers full prefill.
This is a plausible mechanism for the observed refill. Its exact token mismatch
has not yet been reproduced; do not claim that all refills have this cause.

`probes/prefix_replay/ReplayRetentionTests.swift` demonstrates the existing cache
lifecycle with two distinct accepted call signatures. It is an unexecuted test
for an isolated server test target. First run that test against the current
implementation, then reproduce a noncanonical tool spelling across two replies
through the actual template renderer/tokenizer, without a model if possible.

If confirmed, test an opt-in history cache with at most 64 entries and 1 MiB of
charged UTF-8 payload plus explicit per-entry/call metadata charges. Oversized
entries and evictions must fall back to canonical rendering, never reject work.
Retain strict IDs, call order, types, function names and canonical argument
matching; additionally bind replay to visible assistant content in history mode
so edits cannot be ignored. Preserve original single-entry behavior when off.
Only accepted model replies are eligible for storage. Cover edited arguments,
content, IDs, multiple-call order, duplicate signatures, byte/count eviction and
oversized-entry invalidation in tests. Keep this separate from the frozen
AW-0044 candidate and preserve P1.

Physical premise: retaining bounded text might remove redundant full-model
prefill and its expert reads, without snapshots of recurrent/GPU state or any
restriction on agent work. Count storage/heap/encoding overhead, actual avoided
prefill and disk traffic, and complete agent wall. Matching typed calls alone
does not prove identical token trajectories: compare rendered tokens and then
accumulated behavior. No held-out exposure, scoring change or promotion follows
from this source inspection.
