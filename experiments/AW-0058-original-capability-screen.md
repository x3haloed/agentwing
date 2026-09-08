# AW-0058 — Original-suite capability preservation screen

The AW-0047 exact overlap/streaming/history candidate retains a successful
fixed-path recovery comparison (AW-0048) but has not established original-suite
preservation. AW-0049's failed expanded multi-file attempt and all other negative
arms remain authoritative. AW-0052–57 modified sampling/representations are not
included here. Test the unchanged AW-0047 candidate on the complete original
eight-task suite as the next cheap capability gate before larger comparisons.

Primary metric: eight accepted original-task successes out of eight. Manifest
order, prompts, task files and frozen verifier stay unchanged. Stop at the first
utility failure or host/protocol failure, retain it, and label the remainder
unattempted. A failure rejects this screen; a pass only permits further
comparisons. It cannot establish relative speed or erase previous failures.

Use `spec/joint-development-candidate.json`: unchanged q8 model, 0.5-GiB cache,
P1 prompt, sampling, 512-token output ceiling, bash permissions and protocol
normalizations. No model or runtime rebuild. Fresh server and Pi per task;
fixed live workspace path with archive-by-rename after owned processes stop.
The frozen original harness used a suite-lived server and varying workspace
paths, so historical timings are not a matched causal comparison. Any later
comparison must apply the same declared staging/startup policy to both arms.

Use 900-second original task timeout, 60-second readiness cap and existing
pressure/swap gates. Run the unchanged original grader against an independent
temporary copy, with owned process-group cleanup and a 90-second enclosing
deadline (each original command check retains its 60-second limit). Include
startup, task staging, tools, grading and failures in screen wall; static
admission checks precede that clock and remain separate. This is not final
promotion cost accounting. Preserve all transcripts, artifacts and receipts.

Freeze source, original corpus, verifier, model/runtime/profile and harness
pins before launch. Verify copied grading rejects all pristine tasks and accepts
a positive fixture without changing its source. Original grader limitations
remain; supplemental artifact review is required before any promotion claim.
Expanded held-out tasks remain unexposed; all full-goal gates remain pending.

Command: `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_original_candidate_screen.py --task all --candidate-plan spec/joint-development-candidate.json`.

Status: preparation; no model execution yet.

## Terminal result — original preservation screen failed

The first task completes with valid protocol but utility 0 in 234.655291708
seconds including charged staging/startup/grading. The agent searches selected
source/config extensions, reads only config/defaults.json, writes 1000, reads
it back and stops. README and the production shell override are not inspected;
the required answer is 2750. Four valid calls, no failures or repeats, five
requests, 560 new prompt tokens and 245 generated tokens. No original input
files changed. Pressure 1, zero swap growth. Seven later tasks are unattempted
under the predeclared stop rule.

Independent recursive receipt, frozen input/profile/source/binary, workspace,
protocol, host and copied original-grader replay all pass. This rejects the
candidate's original-suite screen. It does not attribute a regression to the
runtime: unlike the historical P1 results, this used the fixed workspace path
and a fresh server per task. A matched P1/candidate diagnostic is needed to
separate runtime effects from those conversation/setup changes. No acceptance
threshold, prior result or P1 artifact is changed.

Raw: `/Users/chad/Models/agentwing/evidence/AW-0058/20260906T150403.217514Z`.
Receipt: `c2d3969d07a24444b910f72755f858bdbbc8a65cc91d0314e6c4086162baeed2`.
See `evidence/AW-0058-terminal-audit.json` and
`evidence/AW-0058-terminal-result.json`. Processes are terminal and P1 preflight
passes. No model run is active from this experiment; no promotion.

### Evidence description correction

The production override referred to above is `deploy/production.env`, not a
shell script. The frozen file contains `RETRY_DELAY_MS=2750`. The failed search
excluded its extension. Grades, raw evidence and disposition are unchanged.
