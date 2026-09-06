# P2 capability panel v1

This locally authored suite contains 24 tasks: eight development tasks and sixteen
held-out tasks, with three substantively distinct tasks in each of eight categories.
Stage A and P1's frozen acceptance inputs remain unchanged.

The executing model receives only its task prompt and a copy of
`tasks/<id>/input/`. `authorities/`, the manifest, solutions, grader code and
mutation evidence must not enter task workspaces, prompts, training or calibration.
This is evaluation separation, not a claim that P1's read-permissive host boundary
prevents a malicious agent from locating files. Held-out tasks have not been
executed against P1 or a candidate. Authoring and reference validation are not
held-out model tuning. A failed held-out candidate must not be tuned and requalified
on the same panel; follow spec/p2-acceptance.json.

`verify_p2_task.py TASK WORKSPACE` grades a temporary copy against an external
Python authority. Workspace symlinks fail closed. Owned grader process groups are
drained on completion or timeout. Agent-modified visible tests are not the success
authority. Where prompts encourage regression coverage, utility currently measures
documented behavior rather than the quality of newly authored tests.

`audit_p2_suite.py` requires pristine failures, reference passes and syntax-valid
incomplete-repair failures. It also removes visible test_*.py files and rechecks
broken inputs; the audit records how many were removed so zero-file cases are
not presented as meaningful test-tampering coverage. Some tasks use maintained
spec_ checks, checked byte-for-byte by the external grader.

`freeze_p2_suite.py` verifies the corpus receipt, all authorities, grading source,
acceptance contract and the full authority-audit result. It rejects changed or
additional files. The receipt is created once; changes require an explicit new
version rather than silently rewriting the freeze. **This freezes the corpus,
not a full-path runner or candidate comparison.** Runner integration and P1
measurements remain outstanding.

These are unfamiliar local task repositories for the executing model, not a
sample of independent real-world repositories or proof of universal generalization.
The longer-investigation category requires tracing incident evidence into a
general repair; actual agent interaction length has not yet been measured.
