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

1. Finish observing AW-0016's `08-config-sync` trial. At 22:35 UTC on
   2026-09-04 it was confirmed live: exec session `16815`, runner PID `59323`,
   server PID `59376`, evidence directory
   `/Users/chad/Models/agentwing/evidence/AW-0016/20260904T222719Z`.
   These are observation handles, not proof of continuing liveness: poll the
   session or inspect processes before taking action. Do not restart a live
   trial. The run has written correct config but has not yet completed; one
   192-token truncation caused salvage and a refill. Wait for the original
   900-second timeout or completion and preserve the final evidence.
2. If AW-0016 passes its first task, run `02-single-file-fix` with the same
   sampler arm and then consider the full suite. If it fails, preserve that
   result and isolate the remaining output-boundary problem. A possible next
   arm stops after a complete tool-call closing delimiter while retaining the
   exact committed prefix; ordinary stripped stop sequences currently reset
   reuse and are not an equivalent implementation. A larger output budget is
   a separate option, not a presumed fix.
3. Address enforceable tool permissions before promotion. A working directory
   and Pi startup-offline mode do not establish a sandbox.
4. Screen alternate configurations, bounded tool results/history, and
   TurboQuant/PolarQuant KV compression as profiling warrants. The inherited
   preference for KV compression is retained; these short trajectories have
   not demonstrated KV pressure as their bottleneck.

## Latest goal-turn evidence

- AW-0015 environment guidance failed: zero utility, timeout, unconfirmed
  cancellation drain. The guard stopped the suite; no process remained.
- AW-0016 found that the greedy hard trigram ban blocks ordinary loopback
  literals, three-parameter typed signatures, repeated paths, and tool markup.
  Swiftlet `97e0bbe` adds an explicit `--allow-repeated-ngrams` arm, leaving all
  other sampling controls unchanged. It is exported as patch 0008 and pinned.
- Full Swift tests (177), both Pi protocol fixtures, and Python tests pass.
- Corrected the inherited KV estimate: 10 full-attention layers with FP32 GPU
  buffers plus CPU mirrors. See `docs/KV_MEMORY.md`; no cache code changed.
- No configuration is promoted yet. The active goal remains unfinished.

The user subsequently activated the long-horizon goal, explicitly specifying
two interleaved replications. The 2026-09-04 goal-contract revision in
`docs/VALIDATION_PROTOCOL.md` supersedes the earlier five-replicate note for
this local promotion. Broader held-out and external-validity work remains
separately labeled. The active goal also authorizes measured reclamation of
reproducible project-scoped data; preserve provenance and record recovery
commands. At continuation, 304 GiB was available, so no reclamation was needed.
