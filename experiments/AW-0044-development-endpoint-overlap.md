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
pinned candidate. It ended after 1181.981 seconds with utility 0, wrong evidence
set, and a model error on the final request: `expert cache budget fits 160
physical slots; batch requires at least 161`. Protocol fails `no_model_error`
and `terminal_metric`. Pressure stays 1 and swap growth 0. Integrity/grader replay
pass, which certifies the failed record, not candidate acceptance. Its shorter
duration is not a speedup result. The original P1 cache also requires the entire
requested batch to fit, so this run alone does not attribute the 161-expert route
union to changed arithmetic rather than different context/path tokens.

C2 (P1) started at
`/Users/chad/Models/agentwing/evidence/AW-0044/20260906T081848.364672Z` and is
complete: utility 0 in 1476.436 seconds, protocol pass, pressure 1 and 0.75 MiB
peak swap growth. It also fails the required evidence set, with ten valid tool
calls and no failures or repeats. Its final request re-prefills 2234 tokens after
2046 prefix tokens match, with zero reused tokens and 599.4 seconds TTFT.
Both control processes and the client exited. The three-arm integrity audit
passes in `evidence/AW-0044-comparison-audit.json`. All three utilities are zero;
the candidate/control utility ratio is undefined. The reported elapsed-time
ratio 0.764 is not a speedup because A1 aborted. The control-success predicate is
vacuous with no solved control task and supplies no capability evidence.
Disposition: reject this candidate for promotion; retain overlap as an unresolved
mechanism for repair. Proceed with separate AW-0045/AW-0046 falsifiers.

`scripts/audit_development_comparison.py` is ready for the three completed
arms, including source/configuration pins, ordering, grading and pooled-control
utility-rate comparison. Static admission checks precede this diagnostic's timed
clock; a final promotion runner still needs complete accounting.
