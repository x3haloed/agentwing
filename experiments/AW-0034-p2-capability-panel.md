# AW-0034 — Build and audit the broader capability panel

Status: construction; not frozen and no agent evaluation executed.

Objective: implement the 24-task panel required by spec/p2-acceptance.json,
without modifying Stage A or narrowing P1's tool/model policy. Eight development
and sixteen held-out tasks cover eight categories. Runtime/representation tuning
must not use held-out task outcomes. Freeze the completed corpus and independent
authorities before comparing candidates.

First tranche: three authored development repositories exercise deployment
precedence, interval-algorithm debugging, and API/CLI archived-item pagination.
Each has a separate behavioral grader and reference repair outside task inputs.
The verifier operates on a copy, rejects symlinks and drains its process group.
No heavy model or performance workload runs during authority checks.

Required authority checks: pristine fail; deleting visible tests cannot turn a
broken submission into a success; reference pass; incomplete repair fail.
The interval oracle tests coverage independently of the merge algorithm. The
multi-file grader separately verifies API, CLI and invalid limits. Navigation
requires evidence paths and preservation of original inputs.

This tranche is incomplete: five development and sixteen held-out tasks,
full-path runner integration, corpus freeze, and P1 capability measurements are
still required. Do not interpret authority checks as demonstrated model capability.

## Eight-category development tranche

Added shared money-rounding refactoring, stale-validator recovery, revisioned
CSV aggregation, non-mutating schema migration, and tenant-join investigation.
All eight development authorities reject pristine inputs, reject broken code
with visible tests removed, accept reference repairs, and reject a specific
incomplete semantic repair. Mutated Python sources must parse before their
rejection counts, preventing syntax failure from masquerading as behavioral
coverage. Sixteen distinct held-out tasks remain to be authored and audited.

The first eight-task audit exposed newline escaping mistakes in recovery and
CSV grader fixtures. Invalid sources are preserved outside Git at
`/Users/chad/Models/agentwing/evidence/AW-0034/initial-eight-audit/`.
They were fixed before model evaluation. The corrected full audit passes;
`evidence/AW-0034-development-audit.json` records the final result. No inference
or task-performance measurement was made, and corpus status remains unfrozen.
