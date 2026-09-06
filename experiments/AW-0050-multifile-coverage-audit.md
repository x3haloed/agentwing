# AW-0050 — Audit the explicit regression-coverage requirement

## Status and scope

Verification gap identified while AW-0049 dev-multi-file is still running.
No model/configuration/benchmark change and no supplemental test execution yet.
The frozen AW-0049 grade and stop policy remain unchanged.

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

Open verification limitation; no candidate acceptance or rejection yet.
