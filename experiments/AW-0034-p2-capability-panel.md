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

## Complete corpus and freeze v1

All 24 tasks are now authored: eight development tasks plus two distinct held-out
tasks per category. The complete authority audit passes pristine/reference/semantic-
mutation checks for all 24. Visible-test deletion counts are recorded explicitly;
a zero-file deletion is vacuous, not an anti-tampering result. Held-out task models
have not run, and no candidate has been tuned on held-out outcomes.

Construction caught escaped-newline errors in reference sources and a backspace
instead of backslash in a negative grader case. The failed source snapshots and
failed full audit are preserved under external `AW-0034/heldout-a-construction`
and `AW-0034/heldout-b-construction`; all were corrected before model evaluation.
These are fixture authoring defects, not candidate failures.

The corpus receipt is `evidence/AW-0034-corpus-freeze-v1.json`, SHA256
`d67041e34c10676ed8583d33a9148b2fe1518ea436caba58cb107c46d34ac4b5`.
It pins 215 files including task inputs, independent graders, solutions,
acceptance contract, auditing source and final authority results. A copied-tree
freeze audit accepts identical inputs and rejects a changed manifest, an added
file and a missing grader. It leaves the actual frozen tree untouched.

Disposition: corpus and authorities retained and frozen; full-path runner,
comparison plans and candidate identities remain unimplemented/unfrozen. P1
preflight still passes. Locally authored incident investigations are broader
than Stage A, but no interaction-length or real-world transfer claim is made.
This completes corpus construction, not model evaluation or the active goal.
