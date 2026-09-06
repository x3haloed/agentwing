# AW-0046 — Drain expert windows instead of exceeding cache capacity

Status: isolated implementation passes 18 focused tests after AW-0044 completion.
Retained for full-model boundary validation; no endpoint or promotion claim.
The design and falsifier notes below preceded execution; results follow.

AW-0044 A1 fails when a prefill union requests 161 experts from 160 cache slots.
The existing cache protects the entire batch during selection, so it throws
before fetching that batch. Full-chain execution has already removed the need
to retain routed expert weights until final accumulation: only their completed
down outputs need remain in scratch. Exploit that shorter lifetime without
changing the model, cache budget, task, context capacity or tool permissions.

`scripts/prepare_oversized_union_streaming.py` drafts an opt-in change against
isolated AW-0043 e707647. With full-chain overlap and
`SWIFTLET_STREAM_OVERSIZED_UNIONS=1`, only unions larger than physical cache
capacity are split into windows of at most 32 experts. Each window drains reads
and GPU commands before another can reuse slots. Shared expert and final sum
order remain original. Fully computed chains need no pending buffer dictionary;
gate/up-only mode still retains its buffers. Failure or cancellation abandons
the incomplete chunk rather than publishing partial results.

`OversizedUnionTests.swift` forces one-expert windows on the tiny model, checks
whole-trajectory bit patterns and unchanged memory budget, then cancels after
one completed window and checks fresh-state recovery. This tests scheduling and
lifetime mechanics; it does not reproduce a real 161-expert union. That boundary
still requires a separate real-data/replayed-request test before claiming the
observed A1 failure fixed. A test-only window cap defaults to nil in production.

Windowed LFU requests change tick/eviction granularity on overflow; do not assert
identical cache decisions there. Charge extra submissions, assignment-map work,
reads, cache effects and complete wall time. Existing fit-in-cache unions retain
their original fetch schedule. This draft is independent of AW-0045 replay
history; validate individually before combining. P1 and AW-0044 remain frozen.

Additional source concern to falsify after C2: `ExpertCache.buffers` assigns
`slotKey`/`keyToSlot` during selection, before any batch reads. Selection can
throw for capacity or allocation outside the later read-failure cleanup. A cold
oversized request may therefore leave keys pointing at unfilled buffers, which
could be returned as hits on a later request. This has not been executed or
confirmed; test error recovery using actual valid expert IDs and compare bytes
with an independent reader. Windowing alone must not be claimed to repair this
separate error path. If confirmed, invalidate pending fills on every throwing
exit and retain the failed-control evidence before testing the repair.

## Executed results

Isolated runtime `62e4a084b119f4d975acd768e1e285fe12662093` builds in release mode.
First, 17 window/scheduling/cache/cancellation tests pass. Then the separate
real-cache test requests 161 valid layer-0 experts with the frozen 0.5 GiB budget.
It fails as predicted: 160 entries remain falsely resident, the next expert-0
fetch is counted as a hit, and its bytes differ from an independent disk read.
The failed test and three assertions are preserved in `cache-recovery-before.log`.

`scripts/prepare_cache_fill_cleanup.py` moves pending-fill invalidation into a
defer covering both slot selection and reads. Successful selection/read behavior
is unchanged. With that repair, 18 tests in seven suites pass: zero stale entries,
the recovery fetch is a miss, bytes exactly match disk, and allocation remains
534,773,760 bytes across 160 slots. Tiny-model forced-window trajectories remain
bit-identical and cancellation after a completed window recovers successfully.
The real-cache test loads no full model; this does not yet validate real-model
oversized streaming or reproduce A1's exact routing history.

Logs are under `/Users/chad/Models/agentwing/evidence/AW-0046`; receipt and source,
binary, kernel and log hashes are in `evidence/AW-0046-cache-and-window-tests.json`.
Archived patch reconstructs exact tree
`8bf6d837c690973506ed91bf8df64e1bd9236735`. P1 preflight passes after tests.

Next boundary diagnostic: use one model process per arm with a fixed synthetic
diverse-token prefix and larger diagnostic chunk size to exercise unions above
160. Compare streaming at the production 0.5 GiB budget against a fit-entire-union
reference with a larger diagnostic cache, on the same token/chunk schedule.
Record actual union sizes, complete logits, subsequent greedy routes, allocation,
pressure and swap; require actual overflow and exact accumulated outputs. This
is a functional oracle, not a throughput comparison or capability task, and
does not change production chunk/cache settings. If no oversized union occurs,
the test is inconclusive. Follow with ordinary representative trajectories before
combining with AW-0045 or spending another endpoint run.

## Full-model boundary result

The predeclared C/A/C functional oracle completes at
`/Users/chad/Models/agentwing/evidence/AW-0046/20260906T085900.600713Z`, runtime
`a48dfbc569d9e7d697f18af7dd21f2b5408618cd` (62e4a08 plus diagnostic test only).
All arms encounter five unions above 160; maximum 217. Candidate completes 33
windows at 160 slots/534,773,760 allocated bytes. References use 321 slots/
1,072,889,856 allocated bytes. All nine complete logit arrays, 10,560 route records
per arm, union lists, input IDs and eight greedy continuation IDs match exactly.
Pressure stays 1 and swap growth 0. Independent receipt/config/output checks pass
in `evidence/AW-0046-real-boundary-audit.json`. This synthetic 256-token/chunk
stress check establishes functional streaming beyond actual capacity; it does
not recreate A1's exact request or establish task capability or a throughput gain.
The production candidate still uses 0.5 GiB and its original chunk policy.

Next ordinary-trajectory check is predeclared in
`scripts/probe_streaming_trajectory.py`: reuse AW-0043's Rust-queue and Unicode
development prompts, 64 generated tokens, normal chunk policy, 0.5 GiB in every
arm, sequential C/A/C per prompt, full route/activation captures and host gates.
Candidate enables all overlap flags plus oversized streaming; reference disables
them in the same repaired source. AW-0045 is still separate. Compare exact
outputs/routes/activation records; do not derive task utility from this screen.
