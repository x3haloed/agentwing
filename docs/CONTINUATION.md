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

1. Observe AW-0019's full eight-task screen before launching other model work.
   Confirmed live on 2026-09-04 at 23:20 UTC: exec session `42871`, runner PID
   `74693`, server PID `74744`, evidence directory
   `/Users/chad/Models/agentwing/evidence/AW-0019/20260904T232042Z`.
   Agentwing at launch: `fd05609`, runtime `459b201`. Manifest confirms `all`
   tasks, max output 512, repeated n-grams allowed, and retained call boundaries.
   These handles are not proof of continuing liveness. Poll or inspect; do not
   restart a live trial. Each task retains the 900-second timeout and host gates.
   At approximately 00:26 UTC on 2026-09-05, tasks 01–07 had passed (378, 640,
   731, 802, 656, 515, and 212 task seconds), with zero model errors/rejections/
   salvage. Task 08 was running. Task 05 incurred one full continuation refill despite
   its tool-replay hit; see AW-0025 for the single-entry replay-cache diagnosis.
   IMPORTANT: full-suite launch requires `--all`; default is navigation only.
2. Both AW-0019 development gates passed cleanly. Config task completed in 620
   endpoint seconds; single-file repair in 641. Each scored utility 1, with no
   model errors/rejections/salvage, full continuation reuse, pressure 1 and zero
   swap growth. Both audits pass. Sessions `36265` and `75462` are terminal.
   Mistaken navigation-only launch `20260904T231929Z`, session `57295`, was
   intentionally stopped after manifest validation, with zero utility and 56
   seconds of preserved cost. Its runner/server are gone; see experiment record.
   Audit the full screen after completion with `scripts/audit_stage_a.py`.
   This is not a paired promotion replicate; two interleaved pairs remain.
   AW-0021's relative-cwd extension is prepared but unused. It needs a real Pi
   fixture and explicit runner/hash integration before any endpoint trial.
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

## Prepared and screened follow-ups

- AW-0020 found no immediately usable alternative weights/runtime in known
  local model locations. This is not a global absence or performance claim.
- AW-0021's relative-cwd extension remains optional and needs a real Pi fixture.
- AW-0022 added `scripts/assess_stage_a_pair.py`; ten Python tests pass. It
  checks necessary metrics for one pair, not the entire promotion contract.
- AW-0023's optional 1,024-character result cap was deprioritized: actual hook
  replay saves only 12 tokens across the baseline and 37 on clean repair.
  Source/evidence retained; do not integrate without new material evidence.
- AW-0024's `scripts/run_task_boundary.py` and `config/task-boundary.sb` are
  prepared but unused. They need disposable descendant-process canaries and
  real Pi protocol validation after the live inference run terminates. If
  adopted, explicitly record and apply the same policy to both paired arms.
