# AW-0044 — First development agent comparison for overlap

Conditional on AW-0043 passing its accumulated audit, compare frozen P1,
AW0043-full-overlap, then P1 on the existing `dev-navigation` task. This is the
first unscreened development category after AW-0035's debugging failure; no task
contents, prompt, verifier, timeout, tool boundary or scoring is changed.

`evidence/AW-0044-development-comparison-plan.json` pins the candidate plan,
runner and corpus before any task outcome. `scripts/run_development_candidate.py`
reuses P1 execution and independent grading, limits selection to development
tasks, and checks candidate source, binary and bundled kernel hashes. Only the
server receives the three explicit overlap flags via `/usr/bin/env`; the agent
client retains its original environment and permission boundary. Full wall
includes setup, startup, failed work, tool execution, shutdown and grading.
All model owners are sequential and host gates remain enforced.

Run C1 and C2 without `--candidate-plan`; run A1 with
`--candidate-plan spec/overlap-development-candidate.json`; all use
`--task dev-navigation`. Record their actual evidence directories below as they
complete. Replay each independent grader with `audit_p2_development.py` and
inspect tool traces for productive/failed/redundant work and protocol errors.
Compare verified utility/hour, preserving zeros. A single development task is
neither broad capability evidence nor the replicated full promotion protocol.

## Execution ledger

C1 (P1) started at
`/Users/chad/Models/agentwing/evidence/AW-0044/20260906T073105.428996Z`.
The frozen corpus audit passed and the owned runner is active; task utility and
completion are not yet known. Resume the existing run rather than restarting it.
A1 and C2 have not started. Preserve the planned order and pinned candidate.
