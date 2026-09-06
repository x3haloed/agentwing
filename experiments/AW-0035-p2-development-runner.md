# AW-0035 — P1 on the frozen P2 development panel

Hypothesis: the existing P1 execution/permission path can complete and produce
independently verifiable work on the expanded development tasks. First diagnostic:
dev-debugging. Primary observations: verified utility and complete wall time.
No candidate comparison, held-out execution or promotion claim.

Use scripts/run_p2_development.py with P1's original frozen binary/profile. P2
corpus receipt d67041e34c10676ed8583d33a9148b2fe1518ea436caba58cb107c46d34ac4b5
is verified before launch. One fresh model session and workspace per task; same
local-agent lock, loopback and task boundary. No author/grader files are copied
to the task. P2's frozen 1800-second Pi timeout applies, with startup separately
capped at 60 seconds. Record and charge setup, startup, execution, cleanup and
grading. Host pressure <4 and swap growth <=1 GiB. No other model owner allowed.

Preserve full transcript, runtime logs, task outputs, protocol audit, independent
grading, host readings and recursive hashes outside Git under AW-0035. A client
exit of zero alone does not earn utility. Failed or malformed runs remain recorded.
Protocol audit checks paired unique tool events, bash arguments, fresh model state,
model errors, server tool rejection, terminal metrics and explicit grader-path
access. Tool failures and exact repeated commands are counted; productivity is
not inferred from a successful exit and requires separate transcript review.

Initial no-model tests cover development selection, held-out rejection, valid and
unpaired/duplicate tool calls, model errors and reused state. This runner is a
P1 development diagnostic, not yet a complete paired promotion runner.

## First live run

Launched P1 dev-debugging at
`/Users/chad/Models/agentwing/evidence/AW-0035/20260906T060736.561511Z`.
The run archives exact runner/helper source hashes and copies. Its manifest
records the pre-run repository HEAD; source snapshots cover the new uncommitted
runner used at launch. No input or runtime file was modified during execution.
At the initial checkpoint the process remains active, pressure is 1 and sampled
swap is unchanged. No utility or completed-task claim exists yet.

`audit_p2_development.py RUN` will verify recursive raw hashes, replay the
independent grader, recompute observable protocol checks and reconcile the
aggregate utility and complete-wall denominator after terminal completion.
The initial runner unit checks pass; live validation remains pending.

## Terminal result: first development task fails

The initial run finished normally as an observed model failure: 0/1 utility in
773.7348 seconds, with original windows.py unchanged. P1 made four productive
repository-reading calls and one productive failed test call. It identified the
bugs, then used its full 512-token response budget on a verbose repair that ended
inside a tool call. The server rejected that incomplete response. No repair ran,
Pi exited zero, and the execution/independent-grading gates correctly awarded zero.
There were six model requests, 895 generated tokens and 369.5 reported TTFT seconds.
Pressure remained 1, swap growth 0; both owned processes stopped and P1 preflight
passed. This is a concrete capability limit of the existing profile on one new
development task, not permission to modify P1 or the frozen task contract.

The full evidence/utility replay audit passes in
`evidence/AW-0035-first-development-audit.json`. Its pass means the failure is
correctly recorded, not that protocol or task success passed. Compact observations
and transcript-based call classification are in
`evidence/AW-0035-first-development-result.json`. Held-out tasks remain unused.

Light source preparation (a roughly 5.7-MiB Git clone plus text edits) occurred
while this development diagnostic ran; no model, build or weight-reading experiment
ran concurrently. Do not treat this unpaired run as a clean performance comparison.
