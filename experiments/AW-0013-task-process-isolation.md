# AW-0013 — Enforce task process-tree isolation

## Status

In progress.

## Hypothesis

Launching each Pi task in a distinct POSIX session and signaling its process
group on timeout will prevent descendants from issuing requests after their
task has been verified or the next task has begun.

## Configuration identities

- Control: AW-0008 runner at `9958483`, which signals only the wrapper PID.
- Candidate: process-group runner with a post-stop server cancellation drain.

## Fixed conditions

- Benchmark, endpoint, model, runtime, harness, prompt, tools, cache, timeout,
  and host gates: unchanged.
- Experimental variable: runner process ownership and termination only.

## Primary metric and acceptance rule

Integrity gate: a wrapper and spawned descendant must both terminate from one
group signal. A timed-out model task must leave no Pi process and no request
targeting its workspace after the next task begins.

## Cheap falsifier

Launch a shell that spawns `sleep 60`, signal its dedicated group, and prove
both parent and child disappear within five seconds.

## Commands

```sh
/usr/bin/python3 -m unittest -q tests.test_exec_process_group
AGENTWING_TASK_TIMEOUT_SECONDS=30 \
AGENTWING_TOOL_PROFILE=shell \
AGENTWING_SALVAGE_TOOL_PREFIX=1 \
AGENTWING_PROMPT_PROFILE=compact-shell \
  ./scripts/run-aw-0008.sh --all
```

## Results

The synthetic regression passes: a wrapper shell and its `sleep` descendant
both terminate from one process-group signal. A second regression verifies the
helper changes to the requested task working directory before exec. The runner
adds bounded TERM-to-KILL escalation, asserts that the process group is empty
after wait, aborts on a leak, and drains Swiftlet cancellation before starting
another task. Model-run isolation verification remains pending.

The model-run falsifier uses `AGENTWING_TASK_TIMEOUT_SECONDS=30` across all
eight tasks. This override is recorded in the run manifest and is for process
integrity only; it cannot produce a performance score comparable to Stage A's
frozen 900-second protocol.

The first 30-second model falsifier (`20260904T185037Z`) crossed all eight task
boundaries without a leaked process group, foreign workspace reference, memory
pressure, or swap growth. It also showed that Swiftlet's terminal cancellation
metric can arrive after the runner snapshots a task log. The runner now blocks
the next task on a terminal-metric barrier captured at termination time and
records whether that drain was observed.

## Confounders and deviations

The synthetic child-tree test does not itself prove Swiftlet cancellation;
model-run log ownership must also be checked on the next multi-task run.

## Evidence

The invalid `20260904T164953Z` run is retained under AW-0008 evidence.
First isolation diagnostic `20260904T185037Z`: summary SHA-256
`79df64b2458fe9f2b37148c56962d24d574cf6a1410260a1464a0ac0d4049ee7`.

## Conclusion

Pending.

## Disposition

Unresolved.
