# AW-0043 — Full prefill expert chain overlap

Test whether computing gate/up/SwiGLU/down as each known union expert read
completes improves on gate/up-only overlap. Keep original per-expert token-batched
GEMVs. Add an indexed SwiGLU batch with the original arithmetic and a uint4 table
of token/pick offsets; split tables at 256 entries to respect Metal's 4096-byte
inline-argument limit without narrowing supported context. One command per expert
retains all data until completion. Shared expert and ordered weighted sums stay
deferred, and routed stages are skipped there only when already completed.

Isolated AW-0043 descends from AW-0042 f0ae501. Opt-in full prefill flag is
`SWIFTLET_CHUNK_FULL_OVERLAP=1`; single-token overlap remains enabled separately.
First run tiny-model chunk/decode bit-pattern and cancellation/recovery tests,
plus inherited cache and partial-overlap regressions. Then repeat AW-0042's two
64-token development C/A/C comparisons with common accumulated capture. Require
exact corresponding input/weight checkpoints, routes, cache decisions and text.
Compare full process, prefill and decode wall to neighboring original controls;
cross-experiment timing cannot isolate the increment over AW-0042.

Charge additional activation dispatches (one per union expert instead of one per
pick index), offset-table construction, command objects, all read/compute waits
and host pressure. No expert byte, cache capacity, installation or codec change.
Retain raw failures and source hashes; P1 and the frozen capability panel remain
unchanged. Passing a component comparison cannot promote this candidate.

## Result — retained for development endpoint measurement

Revision `e707647e9139dbcca86403a1e0a06a705ddabaa3` builds and passes 15 focused
tests in five suites, including indexed-chain chunk/decode bit-pattern parity,
cancellation after submission and fresh-state recovery. Patch reconstruction and
build/kernel/server hashes are in `evidence/AW-0043-build-and-tests.json`.

Raw run: `/Users/chad/Models/agentwing/evidence/AW-0043/20260906T072517.665454Z`.
Receipt SHA256: `5372b816d5018f631d8948a2e5d1ebc03b2c2b89b78e7e521760f2e789e1c022`.
All six 64-token arms complete. All 171 corresponding accumulated input/weight
records match exactly, as do full text, routes and LFU decisions. Historical
coverage therefore matches AW-0042. Pressure remains 1, swap growth 0; candidate
preflight and the 215-file frozen corpus audit pass afterwards.

| Case | Full wall ratio | Prefill ratio | Decode ratio |
| --- | ---: | ---: | ---: |
| Rust queue | 0.8417 | 0.8948 | 0.8301 |
| Unicode records | 0.8702 | 0.9090 | 0.8210 |

Ratios use neighboring-control means. Full-process speedup is approximately
1.19x/1.15x, still below 1.25x and not a utility measurement. This gives a modest
observed improvement over prior diagnostics, but cross-run cache/startup variation
prevents attributing that increment solely to the full-chain change. Retain this
exact candidate for the development-only AW-0044 agent comparison, which can
measure whether the runtime benefit survives actual tool-driven work. No promotion.

Audit: `scripts/audit_full_chunk_overlap.py`; summary:
`evidence/AW-0043-full-chunk-results.json`. Logical bytes are unchanged and all
extra indexed activation dispatches, tables and command overhead remain charged.
