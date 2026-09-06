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
Completed with utility 0 in 1617.620 seconds (26.96 minutes). Client completion,
protocol, pressure 1 and zero swap growth all pass; independent grading rejects
the evidence set because the answer cites `config/edge.json` instead of required
`deploy/launch.sh`. Preserve this failure. All 11 tool calls are valid: three
discovery searches, six source reads, an answer write and its readback. No tool
errors or repeated commands were reported; reading back the answer did not catch
its semantic evidence error. Integrity and grader replay pass in
`evidence/AW-0044-C1-audit.json`; summary in `evidence/AW-0044-C1-result.json`.

The last request reports 2425 new prompt tokens, zero reuse despite 2237 matched
prefix tokens, 193 generated tokens, and 654.1 seconds to first token. Source
inspection confirms tools require the entire cached-token sequence to match;
there is no partial-prefix state rollback on this branch. The cause of this
specific mismatch remains untraced. It is a concrete future work-removal target,
not grounds to alter this comparison's fixed candidate midstream.

A1 started at
`/Users/chad/Models/agentwing/evidence/AW-0044/20260906T075848.611936Z` using the
pinned candidate and is active. Resume it rather than restarting. C2 has not
started. `scripts/audit_development_comparison.py` is ready for the three completed
arms, including source/configuration pins, ordering, grading and pooled-control
utility-rate comparison. Static admission checks precede this diagnostic's timed
clock; a final promotion runner still needs complete accounting.
