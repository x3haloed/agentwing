# AW-0054 — Full-task development screen with bounded-call guidance

## Hypothesis and scope

Generic guidance to split long edits across complete tool calls, combined with
zero frequency penalty, allows the agent to finish dev-multi-file with valid
protocol and requested regression coverage at the original 512-token response
limit. This tests the whole autonomous task instead of another saved suffix.
It is a candidate-only development screen of a declared combined change, not
causal attribution to the prompt alone and not a promotion comparison.

## Fixed conditions and declared changes

Preserve frozen P1, corpus, grader, tool surface, permission boundary, model,
q8 representation, 0.5 GiB cache, 1800-second task deadline, 60-second startup
limit, response budget 512 and the stable live workspace path. Use AW-0051's
joint runtime and sampling observer in an isolated worktree. Add an explicit,
default-off --zero-frequency-penalty server flag; all other sampling options
remain unchanged. Tests must prove the default stays 0.5 and the opt-in changes
only frequency penalty. Preserve all source/binary/patch identities.

Append a task-independent instruction to the frozen system prompt:

> Each response has a 512-token limit. Keep each tool call complete within that
> limit. Split long edits into several small tool calls, continuing until all
> requested changes and validation are complete. Do not omit requested work to
> fit one response.

No task solution, grader detail, Boolean-limit hint, test names or reduced
requirements are added. All original prompt text remains, and the additional
instruction permits multiple calls when a single command would truncate.
The prompt is part of the changed candidate configuration, explicitly pinned
and copied into the raw record. Do not claim prompts match frozen P1.

## Primary metric and acceptance for this development screen

Run the complete frozen dev-multi-file task once with the candidate. Require
accepted utility 1 from unchanged protocol/execution/grader checks, plus direct
evidence that requested regression tests were added and meaningful validation
was performed. Check final artifacts independently; a passing functional grader
without requested coverage is insufficient. Use AW-0050's supplemental coverage
audit on preserved copies, with its costs reported separately and no retroactive
rewriting of the frozen score. Preserve the complete transcript and distinguish
failed tools, malformed calls, repeated commands and final validated success.

Time all startup, model, tool and verifier work in the existing development
runner. Supplemental review costs remain explicit; no comparison rate or broad
speed claim is authorized. AW-0049/AW-0051 failures are historical negatives,
not contemporaneous controls. Do not execute held-out tasks in this screen.

## Cheap checks, launch and stop

Before model execution, build release with two jobs, test options parsing plus
existing session/observer/protocol behavior, and run candidate/P1/corpus preflight.
Freeze prompt, runtime, server, kernel, runner/helper and corpus pins. Launch
only one model owner; retain strict pressure >=4 and swap growth >1024 MiB stop
gates. Stop after this single task regardless of outcome. No prompt/timeout/
verifier changes mid-run and no automatic extra trials. Preserve failures.

## Interpretation and acceptance compatibility

Success would retain a full-task candidate for broader development testing,
not demonstrate general capability preservation or the >=25% goal. Failure
rejects this exact combined candidate on this task. Current P2 acceptance's
matched-prompt/sampling condition remains unchanged; a future promotion design
must explicitly resolve changed candidate settings while retaining frozen P1
as the anchor and every performance/capability/host/protocol/permission gate.
No source or scoring change to sealed benchmarks is permitted by this plan.

## Status

Preparation; no model attempt yet. Identities and test results pending.

## Preparation underway

Isolated runtime `Swiftlet-AW0054` adds the explicit default-off server option
and an options test that checks all other generation settings remain unchanged
for greedy and stochastic requests. A release build with two jobs and focused
options/session/observer tests is running; results are not yet established.
The separate development runner pins/copies the new prompt and replaces the
actual Pi --system-prompt argument while retaining the original boundary.
No model run has started and no candidate binary is frozen yet.
