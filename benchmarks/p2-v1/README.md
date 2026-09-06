# P2 capability panel — construction in progress

This is a new suite. Stage A and P1's frozen acceptance inputs are unchanged.
The campaign requires 24 tasks: eight development tasks and sixteen held-out
tasks, with three distinct tasks in each of eight categories. The current
manifest contains all eight development tasks, and no held-out tasks. **Do not freeze or use this
partial corpus for a promotion claim.**

The executing model receives only its task prompt and a copy of
`tasks/<id>/input/`. `authorities/`, the manifest, solutions, grader code and
mutation evidence must not be copied into its task workspace or supplied to
training/calibration. This is evaluation separation, not a claim that P1's
read-permissive host boundary prevents a malicious agent from locating files.

`verify_p2_task.py TASK WORKSPACE` grades a temporary copy against an external
Python authority. Workspace symlinks fail closed. Grader process groups are
terminated on completion or timeout. Agent-modified visible tests are not the
success authority. Development prompts encourage regression coverage, but utility
currently measures the documented behavior, not quality of newly authored tests.

`audit_p2_suite.py` requires pristine tasks and test-deletion attempts to fail,
reference repairs to pass, and targeted incomplete repairs to fail. Debugging
also has a deterministic integer-coverage property oracle; multi-file work
checks API and CLI separately; navigation checks evidence paths and unchanged
inputs. These fixtures are authored locally and are unfamiliar to the executing
model in this campaign; they are not independent real-world repository samples
or proof of universal generalization.

Before freeze: complete both held-out tasks per category,
audit independent authorities, freeze input/authority/source hashes, integrate
full-path run evidence, and establish a P1 control. Held-out variants must be
substantively different tasks, not development fixtures with renamed constants.
