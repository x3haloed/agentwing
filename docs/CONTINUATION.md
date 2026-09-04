# Continuation state

Ownership transferred from the idle Codex thread **Evaluate maximum local
agentic speed** (`01a06974-8ce6-7ef1-8307-10f3fadb9e04`) on 2026-09-04.
The repository and external evidence are the continuation authority. No model
process was running at takeover. The prior 12 local commits were preserved.

## Completed during takeover

- Recovered and audited the previously unrecorded full Stage A run.
- Recorded its 3/8, 2.064615 utility/hour floor in AW-0008 and LEARNINGS.
- Added a repeatable offline auditor with copied-workspace verification.
- Tightened cancellation handling and completed AW-0014's real-model timeout
  diagnostic: terminal metric observed, no residual process, no swap growth.
- Preserved all benchmark inputs, verifiers, runtime patches, and acceptance
  thresholds.

## Next bounded work

1. Observe AW-0019's `02-single-file-fix` trial before launching any model work.
   Confirmed live on 2026-09-04 at 23:08 UTC: exec session `75462`, runner PID
   `70676`, server PID `70726`, external evidence directory
   `/Users/chad/Models/agentwing/evidence/AW-0019/20260904T230812Z`.
   Agentwing at launch is `fcc5a3c`, runtime `459b201`. These handles are not
   proof of continuing liveness. Poll or inspect processes; do not restart a
   live trial. Configuration is unchanged from the clean config-task result:
   compact-shell, shell-only, salvage enabled, no hard n-gram ban, retained
   tool-call boundaries, max output 512, cache 0.5 GB, timeout 900 seconds.
2. Audit terminal evidence with `scripts/audit_stage_a.py`. If this repair task
   passes cleanly, proceed to a full-suite screen of the same candidate. The
   first AW-0019 gate (`08-config-sync`, run `20260904T225714Z`) finished cleanly
   with utility 1 in 620 endpoint seconds, seven calls, one recovered shell
   failure, zero model errors/rejections/salvage, full reuse, pressure 1, and no
   swap growth. Its evidence audit passes. Session `36265` is terminal and its
   server/runner are gone. Promotion still needs two interleaved full-suite
   pairs, unchanged permissions/scoring, and all host/protocol gates.
3. Address enforceable tool permissions before promotion. AW-0018's native
   sandbox preflight allowed owned workspace writes and the owned endpoint,
   and denied outside writes, symlink escape, and a different endpoint port.
   This is not integrated into Pi and is not a comprehensive sandbox result.
4. Screen alternative configurations, bounded tool results/history, and
   TurboQuant/PolarQuant KV compression as profiling warrants. Short-task
   evidence has not shown KV pressure to be the bottleneck.

## Latest evidence

- AW-0015 environment guidance failed: zero utility, timeout, unconfirmed
  cancellation drain. The guard stopped the suite; no process remained.
- AW-0016 removed the hard trigram ban, which obstructed ordinary code tokens.
  The config artifact passed in 687 endpoint seconds, but the final call was
  truncated and rejected. Pi exited zero despite a model-error reply.
- AW-0017 retained complete tool-call boundaries. The same artifact passed in
  409 endpoint seconds, with full continuation reuse and no salvage. Its last
  call still exceeded 192 tokens. This is a non-interleaved diagnostic, not a
  suite speedup. All AW-0016/AW-0017 processes terminated.
- Swiftlet `459b201` is pinned with nine archived patches. Full Swift tests
  (180 across 29 suites), both Pi protocol fixtures, and six Python tests pass.
- `scripts/verify_runtime_patch_series.py` reconstructs the exact pinned source
  tree using a temporary Git index. All nine patch hashes match. Altered hash
  and incorrect tree negative checks reject. See
  `evidence/runtime-patch-reconstruction.json`; this is source reconstruction,
  not a separate clean build or endpoint replication.
- Corrected KV accounting: 10 full-attention layers with FP32 GPU buffers and
  CPU mirrors. See `docs/KV_MEMORY.md`; no cache code changed.
- No configuration is promoted. The active goal remains unfinished.

The user subsequently activated the long-horizon goal, explicitly specifying
two interleaved replications. The 2026-09-04 goal-contract revision in
`docs/VALIDATION_PROTOCOL.md` supersedes the earlier five-replicate note for
this local promotion. Broader held-out and external-validity work remains
separately labeled. The active goal also authorizes measured reclamation of
reproducible project-scoped data; preserve provenance and record recovery
commands. At continuation, 304 GiB was available, so no reclamation was needed.
