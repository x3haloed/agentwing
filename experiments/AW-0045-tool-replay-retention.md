# AW-0045 — Investigate disappearing historical tool spellings

Status: baseline falsifier and 39 focused candidate tests pass after AW-0044
completed. Retained for model/agent validation; no endpoint gain or promotion.
The following design notes were predeclared before execution; results follow.

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

Draft implementation and tests are now staged as probe sources only:
`probes/prefix_replay/ToolReplayCache.swift`, `ReplayHistoryTests.swift`, and
`scripts/prepare_replay_history.py`. They have not been applied to a runtime,
built or executed. The preparation script requires a clean isolated AW-0045
checkout at AW-0043 e707647. History is opt-in; off-mode retains P1's single-entry
logic. The draft charges raw text, visible content, signature UTF-8 bytes and
fixed metadata allowances, distinguishes this from RSS, and invalidates an old
binding before skipping an oversized replacement. Tests include actual
ChatRequest template conversion and edited-content preservation; tokenizer and
model trajectory checks remain outstanding even if these unit tests pass.

`ReplayTokenizerTests.swift` additionally drafts a model-free reproduction with
the real local tokenizer selected by `AW45_TOKENIZER_DIR`. It parses two accepted
spellings, compares the same history before/after the second cache record, and
compares the complete rendered token sequence with explicit accepted raw history.
It must show a changed older history in off-mode and exact retained tokens in
history mode. This is still unexecuted; even a pass would establish the mechanism
on this constructed fixture, not attribution of C1's exact 2237-token mismatch.

## Executed results

Isolated runtime `08433117ca886d4b0c710a500a44a3af97d3bfab` is based on AW-0043.
The baseline one-entry test passes before applying history retention. Candidate
release build and 39 tests in four suites pass, including strict call fields,
canonical arguments, edited visible content, eviction, oversized replacement,
existing protocol checks and the real local tokenizer. No model weights are
loaded by the tokenizer test. Off-mode changes the prior history from 281 to 291
tokens, common prefix 247; full rendering has 334 tokens and differs from exact
raw history. On-mode retains all 281 tokens; full rendering has 324 tokens and
matches exact raw history. This proves the constructed mechanism, not C1/C2's
specific mismatch or any saved model/agent wall time.

The first build failed on copied absolute-path module caches; a repeated attempt
failed identically. `swift package clean` removed only cloned AW-0045 build
products, then local rebuilding passed the baseline. The initial candidate build
caught missing inner `try` in the tokenizer test; corrected before the passing
run. Logs and hashes, source/kernel/server/tokenizer pins and patch reconstruction
are in `evidence/AW-0045-tokenizer-and-tests.json`; raw logs are under
`/Users/chad/Models/agentwing/evidence/AW-0045`. Archived patch reconstructs exact
tree `b71eab0a6e376cba0b4bd3f3dc3a447c79f40a4e`. P1 preflight passes afterward.
Next: validate AW-0046 independently, then choose a declared model/tool-history
trajectory check before another costly endpoint comparison. No held-out exposure.
