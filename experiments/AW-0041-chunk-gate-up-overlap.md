# AW-0041 — Preserve token batching while overlapping chunk gate/up

Hypothesis: submitting each union expert's token-batched gate/up projections as
its read completes reduces prefill time without changing accumulated outputs.
Original batched SwiGLU, down projections, shared expert and final weighted sum
remain in their existing order. This avoids replacing eight strided activation
dispatches with one dispatch per token/pick. It overlaps only part of computation;
read bytes, cache capacity and scratch representation remain unchanged.

Base is AW-0040 `234028121de5fe4d082b3198105466ff34f36cb6`, isolated checkout
`Swiftlet-AW0041`. `scripts/prepare_chunk_overlap.py` reconstructs the change.
`SWIFTLET_CHUNK_OVERLAP=1` opts in; `SWIFTLET_EXPERT_OVERLAP=1` also enables the
previous single-token mechanism. No production P1 edits. Callback/read lifetime
and failure cleanup reuse AW-0040, and all committed commands drain on exit.
At most one command per known union expert; no future routing oracle.

First verify tiny-model multi-chunk boundaries plus subsequent decode logits
bit-for-bit against control, and cancellation during chunk submission followed
by fresh-state recovery. Then repeat the three-prompt C/A/C protocol from
AW-0040, with both overlap flags enabled only in A. Require complete text, route
and LFU decisions to match; inspect prefill, decode and full-process wall plus
sampled disk bytes/footprint. Pressure 4 or >1 GiB swap growth rejects the run.

No capability tasks or held-out exposure yet. Short timing runs, phase counters
that omit overlap command attribution, and OS cache variation cannot establish
the goal. A survivor needs longer/uncommon trajectories and endpoint comparisons.

## Result — retained for longer accumulated-trajectory validation

Isolated revision `d44752e26afbe7d469e425694224c11830ddd5f4` builds and passes
13 focused tests in four suites. The first build exposed missing cancellation
propagation into the inner chunk method; its source and log are preserved. After
passing the closure through, cancellation after a submission and fresh-state
recovery pass, as do multi-chunk prefill plus subsequent decode bit-pattern
comparisons. The archived patch reconstructs the runtime tree; build/test hashes
are in `evidence/AW-0041-build-and-tests.json`.

Raw run: `/Users/chad/Models/agentwing/evidence/AW-0041/20260906T070759.500426Z`.
Receipt SHA256: `b91c51f6ddc48cf2e7ee14a460d98fe4b469c9daa82b44e269bc2106fb284605`.
Nine C/A/C model runs completed. The receipt audit and full text/route/fetch-miss
comparisons pass. Candidate ratios to neighboring-control mean time:

| Case | Full process wall | Prefill | Decode |
| --- | ---: | ---: | ---: |
| Coding | 0.8100 | 0.9046 | 0.7918 |
| Arithmetic | 0.8212 | 0.9125 | 0.8078 |
| Structured | 0.8146 | 0.8923 | 0.8190 |

Observed process disk reads span 12.33–16.45 GiB/arm and sampled footprint
2.615–2.646 GiB. Pressure stays 1, swap growth 0, post-run P1 preflight passes.
Logical expert read bytes remain identical within cases. Readiness submission
adds bounded command objects but no expert representation or cache allocation
change, codec, installation pass or persistent artifact conversion. This does
not reduce expert bytes; physical traffic and command overhead stay charged.

Full-process speedup is approximately 1.218–1.235x here, below the 1.25x goal and
not an autonomous utility measurement. Startup and process disk variation remain
confounders; this run alone does not isolate the incremental effect relative to
AW-0040, although its own off/on/off comparisons test the combined candidate.
Retain for longer and uncommon trajectories with accumulated activation checks.
Do not promote or expose the held-out panel on these short results alone.

Audit: `scripts/audit_chunk_overlap.py`; machine-readable summary:
`evidence/AW-0041-chunk-overlap-results.json`. Phase attribution inside overlapped
commands remains incomplete; only whole prefill/decode/process times are used.
