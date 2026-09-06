# AW-0052 — Captured-input frequency-penalty counterfactual

## Status

Probe preparation; no model run yet. All source/binary/input/runner identities
must be frozen before execution. This record is not the launch manifest.

## Hypothesis and primary diagnostic

Removing the frequency penalty prevents the repeated, incomplete tool-generation
suffix on AW-0051 request 13 without raising its 512-token budget. First require
an unchanged 0.5 fresh-prefill control to reproduce the original 512 generated
IDs and emitted text. If it differs, stop this sequence and preserve the result;
fresh-prefill state is not an adequate counterfactual for the cached failure.
If it matches, run penalty 0 then a second 0.5 control in separate processes.
Both controls must match the original. The zero arm must terminate with a
complete valid declared bash tool call within the original budget to support
the diagnostic hypothesis. Independently inspect the resulting command and
regression coverage; token length alone is not success. Do not execute generated
commands in this model-only probe. Endpoint utility remains unmeasured.

## Fixed conditions and implementation

Use AW-0051 runtime e781ebeb6c77101dbf845419c5ece099d1d1e4d2 in a separate
worktree. Add only a test target source; use the existing dependency-injected
session constructor with the real QwenMetalModel and real tokenizer. Supply
exact captured input IDs through the render closure, with no re-encoding,
chat-template substitution, task hints or runtime sampler edits. Restore all
captured sampling, suppression and stop settings, changing only frequency
penalty in the declared zero arm. Each process starts with fresh model state,
0.5 GiB expert cache, identical joint overlap flags and read-only sampling trace.
Use the pinned Qwen qpack on the fixed 16 GB M1/internal SSD. P1, original
candidate and all sealed benchmark and acceptance files remain unchanged.

Input: external AW-0051 analysis request-13-input.json, SHA256
`ddad2cf7529bd1bb5a7fc81cae04a6eee4b3d3e25f11df77661a77d288bfe5ac`.
Original cached request had 2198 reused + 21 new prompt tokens; this probe
fresh-prefills all 2219, an explicit potential numerical/order confounder.
Raw-token input bypasses only rendering, not generation or stop logic.

## Gates and limitations

Before model execution, build release with two jobs and run existing focused
sampling/session tests. Supervise one process group, sample pressure/swap,
stop at pressure >=4 or swap growth >1024 MiB, and enforce 1800 seconds per arm.
No concurrent model or build. Preserve every attempt and hash all evidence.
Stop after failed control reproduction or host violation; expected zero-arm
protocol failure is a negative result, not a reason to modify settings mid-run.
No speed or promotion claim from model-only replay. The frozen P2 acceptance
requires matched sampling across compared arms; a future candidate with changed
sampling needs an explicit comparison design that respects that requirement.

## Disposition

Unresolved, development-only. Held-out tasks remain untouched.

## Build and frozen launch plan

Release build and 53 focused tests in eight suites pass. Initial compilation
failed on nested Testing macros in the new probe; split the requirements and
retained both logs. Runtime production sources are unchanged from AW-0051.
Source patch, test binary, kernel, input, harness helpers and runtime identity
are pinned in `evidence/AW-0052-replay-plan.json`; build evidence is in
`evidence/AW-0052-build-tests.json`. Each control is checked automatically
against original generated IDs and text before the next arm can run.

Command: `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/probe_sampling_replay.py`.
The probe adds no executable tools or network listener. Output content requires
independent protocol/coverage review before interpreting a completed sequence.

## Initial launch stopped; supervision corrected

First C1 stopped at 39.03 seconds after observing SwiftPM's testing helper in
PGID 74249 outside wrapper PGID 73849. Explicitly terminated the observed helper
group; wrapper/supervisor exited, both process IDs are gone, preflight passes.
Pressure 1, swap growth 0. Preserve this as a supervision failure, not a sampling
result. Raw run `AW-0052/20260906T124616.055538Z`; receipt and reason are recorded
in `evidence/AW-0052-initial-launch-stop.json`. Initial frozen plan is archived.

Revised launcher executes that same helper directly as the owned process-group
leader, with pinned Xcode Testing framework path. The first direct smoke exposed
a missing framework search path; the corrected empty-filter smoke loads with
zero tests (exit 69), and actual SamplingTraceTests then pass with exit 0.
Preserve these logs. Revised plan pins helper and framework as well as prior
identities. All model/sampling/input conditions remain unchanged.

## First control completes and reproduces original failure

Revised run `AW-0052/20260906T124847.512867Z` C1 completed in
725.218569542 seconds, exit 0, pressure 1, swap growth 0. All 512 generated IDs
and emitted text match AW-0051 request 13 exactly. Independent decision audit
finds no sampling anomalies. This validates the fresh-prefill control for this
captured trajectory; test exit 0 denotes successful reproduction of a rejected
output, not autonomous task success. `evidence/AW-0052-C1-trace-audit.json`
records hashes of the completed arm; whole-run receipt remains pending.
The frozen supervisor advanced to A1 with frequency 0, verified as its own
process-group leader. C2 and full comparison/content audit remain outstanding.

The completed C1 also matches every recorded selected raw/adjusted score,
bounded raw/adjusted candidate summary, seen count and EOS-mask decision across
all 512 positions. Maximum selected raw-score absolute difference is 0. This
strengthens the observed replay equivalence without asserting full-logit or
hidden-state identity. Trace hashes and field counts are in
`evidence/AW-0052-C1-observed-score-comparison.json`.
