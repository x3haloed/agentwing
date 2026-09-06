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
