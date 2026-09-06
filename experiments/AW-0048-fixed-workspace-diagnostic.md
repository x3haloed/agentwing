# AW-0048 — Fixed workspace path in the recovery comparison

## Status

Planned. Lifecycle and existing-boundary engineering checks pass; no model arm
has run. AW-0047 remains terminal and negative, with no promotion.

## Hypothesis

Holding the model-visible workspace and private-state paths constant removes
the concrete path-text confounder found immediately before the first divergent
recovery repairs in AW-0047. The testable behavioral prediction is that the two
P1 controls produce the same visible transcript through their first repair when
their preceding visible inputs agree. Failure of that prediction rejects path
variation as a sufficient explanation. Agreement cannot establish exact wire
token identity or prove that path variation caused the earlier failures.

## Configuration identities and fixed conditions

P1 remains the immutable control from `spec/validated-local-agent.json`.
The unchanged candidate is `spec/joint-development-candidate.json`: AW-0047
runtime 4dff62e867d62288d4224974c4add523dad50437, with full expert overlap,
bounded oversized-union streaming, and strict accepted-tool history retention.
Its earlier failed capability-preservation result remains recorded.

Only the development harness workspace placement changes in both arms. The
generic live path `/Users/chad/Models/agentwing/active/workspace` is selected
before outcomes and will not be tuned. The existing boundary gives each attempt
fresh adjacent `/Users/chad/Models/agentwing/active/agentwing-task-state`.
After owned client/server processes stop, both directories are renamed into
that attempt's unique evidence directory. No task input, prompt, model, runtime,
tool schema, permission policy, validator, grader, generation setting, cache
budget, or timeout changes. The same 16 GB M1/internal SSD is used. Manifest
records OS, thermal state, available storage and all source/binary hashes.
The 215-file AW-0034 corpus freeze and P1 checks must pass before every arm.

## Primary metric and acceptance rule

Primary diagnostic: whether the two controls' first repair commands agree after
an identical structured visible prefix. Compare commands, visible assistant
contents without generated call IDs, and exact tool results; retain raw traces.
Report accepted utility and full measured wall time for C1/A1/C2 as secondary
development evidence. A candidate losing a control success fails preservation;
elapsed time without utility never establishes a gain. Compare pooled control
utility/hour only if its denominator is positive. This single-task diagnostic
cannot qualify the project goal or reverse AW-0047.

Frozen order: dev-recovery P1 C1, unchanged joint A1, P1 C2. Stop remaining arms
on host-gate or protocol failure; ordinary grader failure is retained and the
order continues. Task timeout 1800 seconds; server startup capped at 60 seconds.
No held-out model execution. No selecting a more favorable path or repeating
arms to replace failures.

## Cheap falsifier and commands

Before the model comparison, five lifecycle/boundary tests passed: repeated
fresh inputs at the same path, independent workspace/state archives, exception
preservation, refusal of unowned/unfinished contents or archive collisions,
and actual unchanged sandbox execution allowing scoped writes while denying
a test-owned outside write. These are engineering checks, not speed results.
Candidate check-only admission also passed. Neither loads model weights.

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/test_stable_workspace.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_stable_development.py --task dev-recovery --check-only
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_stable_development.py --task dev-recovery
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_stable_development.py --task dev-recovery --candidate-plan spec/joint-development-candidate.json
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_stable_development.py --task dev-recovery
```

Each model arm is launched separately after checking the preceding result and
stop gates. `audit_stable_development.py` verifies all three archived receipts,
grader replay, profile/source pins, actual Pi session cwd, common path policy,
and ordered nonoverlapping execution. Inspect visible prefixes separately.

## Confounders and accounting

Static admission precedes the measured diagnostic clock. All subsequent setup,
model/tool execution, workspace archival and grading enter that clock, but this
is not the final promotion accounting runner. OS cache/thermal variation and
unrecorded raw wire spellings remain possible confounders. Fixed paths control
one observed difference; they do not guarantee deterministic model behavior.
The test is selected using development evidence, so it provides no held-out
generalization estimate. Prior demonstrated successes remain regression gates.

## Evidence and disposition

Frozen pins: `evidence/AW-0048-fixed-workspace-plan.json`.
Large raw evidence: `/Users/chad/Models/agentwing/evidence/AW-0048/`.
Engineering log: `workspace-tests.log`, with its hash in the frozen plan.
Unresolved pending the declared comparison. No candidate promotion.
