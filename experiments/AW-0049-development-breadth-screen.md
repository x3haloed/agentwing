# AW-0049 — Development breadth after fixed-path recovery

## Status

Prepared while AW-0048 C2 runs. No AW-0049 model attempt or preflight yet.
Launch depends on AW-0048 completing its frozen order and terminal audits.

## Hypothesis

The unchanged joint runtime can complete valid autonomous tool trajectories on
the remaining frozen development categories, beyond the successful recovery
example, without exceeding the existing host gates. This is a breadth screen,
not a throughput comparison or a claim that every task must be solved to meet
the project goal.

## Configuration identities and fixed conditions

Candidate: unchanged `spec/joint-development-candidate.json`, with the exact
AW-0047 source, binary, kernel resource and five environment flags. P1 remains
the immutable control and usable launcher. The runner is copied from AW-0048
with only its experiment output directory and self-snapshot name changed.
The fixed workspace, archive lifecycle, original permission boundary, 0.5 GiB
cache, model, prompt, tools, sampling, 512-token output ceiling, 1800-second task
deadline, 60-second startup deadline and independent grader remain unchanged.
The AW-0034 215-file corpus freeze applies. Manifests record source/binary pins,
OS, hardware, storage and thermal state. One model-owning process at a time.

## Primary metric and acceptance rule

Record accepted task utility and each protocol/host gate across the seven
development tasks not covered by AW-0048. The existing recovery results remain
part of development evidence; final promotion must still include the complete
original and expanded suites in the required replicated comparisons.

Order: dev-multi-file, dev-navigation, dev-debugging, dev-refactoring, dev-data,
dev-migration, dev-investigation. Launch each separately, with a fresh workspace,
private state and server, and inspect its terminal result before advancing.
Start with multi-file because AW-0047 exposed incomplete tool output there.
Stop remaining screen attempts on host-gate or protocol failure, preserving
that failed attempt. Ordinary independent-grader failure is retained and the
screen continues; it may require controls or development repair, and does not
by itself establish regression when the control has not solved that case.

There are no contemporaneous controls in this inexpensive admission screen.
Report candidate timings as costs only, not speedups. No held-out task is run,
no grading criterion changes, and no successful task substitutes for a failure.
The screen cannot promote a successor or reverse AW-0047's negative evidence.

## Cheap falsifier and commands

AST validation of the copied runner is complete. Admission checks must wait
until AW-0048's model-owning processes are terminal. Before each attempt:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_breadth_development.py --task dev-multi-file --candidate-plan spec/joint-development-candidate.json --check-only
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_breadth_development.py --task dev-multi-file --candidate-plan spec/joint-development-candidate.json
```

Substitute the next declared development task only after checking the previous
result. `scripts/audit_candidate_screen.py` combines independent grader replay
with source/profile/path checks and reports protocol success separately from
record integrity. Its implementation pin is in
`evidence/AW-0049-auditor-pin.json`; AST validation passed, while validation on
a completed AW-0049 record is pending. Preserve incomplete receipts and host
stops separately if the completed-run auditor cannot accept them.

## Confounders and evidence

Static admission precedes the measured runner clock, as in AW-0048. Fresh
workspace setup, execution, archival and grading after that clock are charged.
This is not the final promotion accounting runner. OS cache and thermal state
may vary between tasks; different task times are not causal mechanism estimates.
Development selection is informed by prior failures and is not held-out proof.

Frozen pins were committed before model execution in
`evidence/AW-0049-development-breadth-plan.json`. Raw traces belong under
`/Users/chad/Models/agentwing/evidence/AW-0049/`.

## Disposition

Unresolved, pending the prerequisite comparison and declared screen.
