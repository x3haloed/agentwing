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

**LIVE C2:** `20260905T040519Z`, launch revision4831a34, exec session77088,
runner57579/server57634. Frozen plan v2 passed all input hashes. Manifest
common fields match C1; control flags max192, hard ngram3, no retained stop.
Listener127.0.0.1:8080 verified. Evidence:
`/Users/chad/Models/agentwing/evidence/AW-0027/20260905T040519Z`.
Poll this existing session; no runtime edits/builds or concurrent models.
After terminal audit C2, then launch A2 with the unchanged v2 plan.

C2 checkpoint at 2026-09-05 05:06 UTC: task06 failure recovery is active.
Task01 passed in610 seconds; tasks02/03/04 timed out in908/914/910 seconds,
scored0, and failed artifact verification. All three cancellation drains were
observed. Task05 completed in262 seconds, Pi exited0, but verifier failed and
utility is0. It had1 tool call,0 failed calls,1 model-error reply,1 rejected
output,0 salvage. Preserve this completed failure; do not reinterpret it as a
timeout or change scoring. Task05 transcript SHA256:
3351fab921b3d54cfaa230a117e4d727c4c219fd39d4d78a39dff325d7313545.
Pressure remains1; swap735.50MiB,0.31MiB above starting735.19. Session77088,
runner57579/server57634 remain live; no suite summary or second-pair result.

A1 is terminal and audited:8/8 in4559 endpoint seconds,6.317174819039263
utility/hour. First pair passes at3.670980478175038 times C1. Pressure1,
zero swap growth; session76879 exited0 and both owned processes terminated.
Port8080 confirmed free. C2 is now live as recorded above; A2 follows it.
See `evidence/AW-0027-A1-audit.json` and `evidence/AW-0027-pair-1.json`.

C1 is terminal and audited:3/8 in6276 endpoint seconds,1.7208413001912046
utility/hour, pressure1, zero swap growth. Session10183 exited0; runner3471 and
server3533 are gone. Evidence `AW-0027/20260905T010110Z`. See corrected audit
and preserved original audit. Original observer wrongly required metric as the
last line; same-request known post-generation diagnostics are now permitted.
All13 Python tests pass. No measured execution input or scoring changed.

Use `evidence/AW-0027-frozen-plan-v2.json` for remaining A1 → C2 → A2. Original
plan is retained, and v2 explicitly records the auditor-only amendment. A1 is terminal; do not rerun C1 or modify runtime/runner/benchmark inputs.

1. AW-0024's real-model boundary gate is terminal and audited. Session `44831`,
   runner `98431`, and server `98487` are gone. Run
   `/Users/chad/Models/agentwing/evidence/AW-0024/20260905T004228Z` passed bounded
   reading in 222 endpoint seconds, with pressure1 and zero swap growth.
   AW-0026 clean release build and all 180 tests in 29 suites passed; checkout
   remained clean. All 50 installed qpack payload hashes also matched.
   Evidence: `evidence/AW-0026-clean-build.json` and model payload verification.
   AW-0027 now freezes C1 → A1 → C2 → A2 in
   `evidence/AW-0027-frozen-plan.json`. Launch each full suite using
   `python3 scripts/run_frozen_arm.py evidence/AW-0027-frozen-plan-v2.json SLOT`.
   Do not change frozen execution files or runtime during this sequence.

2. The boundary gate passed. Freeze the comparison
   plan and run two interleaved full-suite control/candidate pairs. Use the same
   scoped permission policy in both arms; the pair checker now verifies this.
   Control keeps compact-shell/shell/salvage, max192, hard n-gram size3, and no
   retained tool boundary. Candidate uses max512, n-gram0, and retained boundary.
   Keep all other model/runtime/harness/cache/task/timeout settings identical.
   Complete reproducibility evidence and required protocol checks before any
   promotion. A numeric screen against the historical floor is not replication.
3. AW-0019's complete eight-task screen is terminal and audited: 8/8 in 4,469
   endpoint seconds, 6.444395 utility/hour, pressure1, zero swap growth, and no
   model errors/rejections/salvage. Its original session `42871`, runner `74693`,
   and server `74744` are gone. Evidence:
   `/Users/chad/Models/agentwing/evidence/AW-0019/20260904T232042Z`.
   The rate is 3.12135 times the historical floor in a non-interleaved comparison.
   One full continuation refill occurred on task05; AW-0025 explains the
   single-entry raw-history replay limitation. Do not silently fix it mid-pair.
4. AW-0024's eleven canaries and real Pi boundary fixture pass, as do the two
   original Pi fixtures and eleven Python tests. Raw boundary fixture evidence:
   `/Users/chad/Models/agentwing/evidence/AW-0024/protocol-20260905T004117Z`.
   See `evidence/AW-0024-protocol-validation.json`. The policy restricts writes
   and outbound connections; reads and other capabilities remain permitted.
5. Full-suite launches require `--all`; default is navigation only. The mistaken
   AW-0019 navigation launch was preserved and stopped, not counted as a suite.
   Optional cwd-hint, output-limit and retained-history arms remain unmeasured
   or deprioritized. Do not add them to a frozen comparison without a new plan.

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
- AW-0022 added `scripts/assess_stage_a_pair.py`; eleven Python tests pass. It
  checks necessary metrics for one pair, not the entire promotion contract.
- AW-0023's optional 1,024-character result cap was deprioritized: actual hook
  replay saves only 12 tokens across the baseline and 37 on clean repair.
  Source/evidence retained; do not integrate without new material evidence.
- AW-0024's task boundary passed descendant canaries, Pi protocol, and real-model
  compatibility. Both AW-0027 arms explicitly enable this identical policy.
