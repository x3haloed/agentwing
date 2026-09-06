# AW-0050 — Audit the explicit regression-coverage requirement

## Status and scope

Complete. The actual artifact has no added tests, and its original test misses
the targeted regression. A synthetic positive control validates detection of
added coverage. No model/configuration/benchmark change; frozen scores remain.

## Requirement and observed gap

The task explicitly requests added regression coverage, and README.md asks for
`python3 -m unittest -q`. The frozen independent grader tests API/CLI behavior
but does not inspect or execute submitted tests. AW-0047 C1's original test
file was unchanged even though its saved implementation earned artifact grade
1; accepted utility was correctly 0 because final tool protocol failed.
This is a concrete coverage limit of the verifier, not a reason to alter that
historical score or infer the still-pending AW-0049 outcome.

## Hypothesis and audit procedure

After the measured run and owned processes are terminal, inspect its archived
test changes and execute the documented unittest command on a disposable copy.
Check whether added tests exercise a relevant regression, using a narrowly
targeted copied-code mutation where supported: ignore the opt-in archived flag
while preserving default behavior. Confirm that mutation actually changes the
intended behavior before interpreting any test failure. The unchanged initial
test suite is a negative coverage control. A supported mutation killed only by
the submitted suite supplies evidence of added coverage for the new option.

This mutation is one coverage diagnostic, not an invented requirement that
every valid regression test must cover that specific branch. Tests may cover
other requested behavior; inspect those cases rather than treating a surviving
mutant as automatic task failure. Unsupported mutation signatures or execution
errors remain inconclusive. A passing functional grader alone is insufficient
proof that tests were added. Keep supplemental results distinct from frozen
accepted utility and identify any incomplete prompt requirement explicitly.

## Boundaries and evidence

Never edit the measured workspace, original task, grader, model prompt or
runtime. Run all follow-up tests in separately owned copies after measured
execution, preserve their commands/results and charge their costs as follow-up
verification rather than retroactively rewriting the frozen run clock.
Final promotion accounting must include its required verification costs.

Scope evidence: `evidence/AW-0050-test-coverage-scope.json`.
Large follow-up evidence belongs under
`/Users/chad/Models/agentwing/evidence/AW-0050/`.

## Disposition

Confirmed missing prompt requirement in the AW-0049 artifact. Its accepted
utility was already 0 for protocol and grading failures; that score is unchanged.

## Results

`scripts/audit_multifile_coverage.py` runs four disposable workspace variants
under the unchanged task boundary after measured model processes stop. The
submitted and original tests both pass with and without the targeted mutation.
The probe confirms that the mutation disables archived-item inclusion while
preserving the tested default and input records. Submitted test sources are
unchanged. This confirms the missing added-test requirement for this artifact;
it does not make one mutation an exhaustive coverage criterion.

A separately labeled synthetic fixture adds one opt-in assertion. Its submitted
suite passes original code and fails the mutant; original tests pass both.
This validates the auditor's positive path without altering actual agent output.
Both source receipts remain intact. Actual follow-up execution costs 0.6864
seconds; all supplemental costs are separately recorded rather than rewriting
the frozen task clock. Raw evidence:
`/Users/chad/Models/agentwing/evidence/AW-0050/20260906T115222.370947Z` and
`/Users/chad/Models/agentwing/evidence/AW-0050/20260906T115557.175099Z`.
Summary/receipt hashes: `evidence/AW-0050-coverage-audit-result.json`.
