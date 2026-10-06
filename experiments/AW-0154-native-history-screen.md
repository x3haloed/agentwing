# AW-0154 — authoritative decoded history proposal screen

Hypothesis: eligible lookup3/proposal3 reduces target verification passes on the
real AW141 failing fourth generation. Primary metric: oracle draft acceptance
and verification-pass count; no timing or endpoint claim.

The AW153 missing fragment is three bytes `3c2022` (less-than, space, quote).
Do not infer its original token sequence. Instead, AW141 verbose server logs
contain 7695 authoritative decoded IDs for task178, at consecutive context
positions1186–8880. The initial1186-token input is the byte-pinned AW148 fourth
request prefix. Use only that logged span, excluding any unlogged final token.

Before replay, freeze source/input hashes and scope in external plan.json.
The fixture copies the unchanged native proposer from AW153 and runs lookup3 /
proposal3 against past history plus current sampled token. Future logged IDs
are used only to verify drafts. No weights, inference or tool execution.
Inherited full runtime/model/harness/native sampling/task provenance remains
in AW141/AW148 receipts; this does not change either configuration.

Result: baseline7694 steps,6168 verification passes,1381 nonempty draft batches,
4143 proposed tokens,1527 oracle accepted,1029 batches with a rejected draft.
An independent Python implementation reproduces all five counts. The ideal
equal-cost pass ratio1.247406 is below1.25, before lookup, rollback and batching
costs. This is not actual speed, an endpoint result, or a universal bound on a
changed kernel. Preserve AW141 utility0 and frozen P1.

Disposition: retained only for complete batched-target/checkpoint cost and
sampling fidelity investigation; no promotion. Exact IDs supersede the missing
stream-fragment recovery barrier, not AW153's valid negative mapping result.
Raw evidence outside Git: /Users/chad/Models/agentwing/evidence/AW-0154.
Manifest and hashes: evidence/AW-0154-native-history-screen.json.
