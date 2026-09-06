# AW-0046 — Drain expert windows instead of exceeding cache capacity

Status: separate draft source and tests; not applied, built, or executed.
Complete AW-0044 C2 and its audit before any follow-up build/model experiment.

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
