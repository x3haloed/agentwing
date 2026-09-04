# AW-0014 — Require a terminal metric at timeout boundaries

## Status

Complete; retained as runner integrity infrastructure.

## Hypothesis

Requiring a complete terminal metric after the recorded stop boundary, and
aborting on an unconfirmed drain, prevents diagnostic log noise from admitting
the next task before cancellation completes.

## Configuration identities

- Control: AW-0013 runner at `d7714ae`, accepting any new server-log line.
- Candidate: terminal-metric parser plus fail-closed suite termination.
- Swiftlet remains `d7352d79ebb13a030bd3eb878510aaed7e9eb5b1`.

## Fixed conditions

Same M1 host, internal SSD, pinned Qwen artifact, Pi, compact-shell prompt,
shell-only tool, prefix salvage, 0.5 GB expert cache, greedy sampling, loopback
endpoint, and frozen Stage A v1.1. Use a recorded 30-second task timeout for
the integrity diagnostic only. This does not create a comparable work-rate
score. Exact revisions and host state are captured by the runner.

## Primary metric and acceptance rule

Integrity, not throughput: stale metrics, ordinary diagnostic lines, and
partial writes must not satisfy the barrier. A missing terminal metric must
stop the suite. A real timed-out task must observe its terminal metric before
the runner exits or admits another task, with no residual task/model process,
critical pressure, or swap growth above 1 GiB.

## Cheap falsifier

Unit fixtures with a stale metric, unrelated new lines, a partial metric,
a complete new metric, and a missing metric. Then one real task at 30 seconds.

## Commands

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover -s tests -q
AGENTWING_TASK_TIMEOUT_SECONDS=30 AGENTWING_TOOL_PROFILE=shell \
  AGENTWING_SALVAGE_TOOL_PREFIX=1 AGENTWING_PROMPT_PROFILE=compact-shell \
  AGENTWING_EVIDENCE_ROOT=/Users/chad/Models/agentwing/evidence/AW-0014 \
  ./scripts/run-aw-0008.sh --task 01-navigation
```

## Results

All six Python tests passed, including stale/noise/partial/complete metric
fixtures and bounded missing-metric waiting. Shell syntax validation passed.

The real-model diagnostic `20260904T203854Z`, at Agentwing `7222887`, stopped
the task at its recorded 30-second timeout and observed a complete terminal
metric before proceeding to verification and server shutdown. Task wall time
was 51 seconds and total endpoint time 56 seconds. The task segment contains
one 480-token initial request, zero reused tokens, and zero generated tokens.
Pressure peaked at 1; peak and final swap growth were zero. No runner,
process-group helper, or Swiftlet server remained after completion.

This intentionally scores zero utility and is only a cancellation diagnostic.

## Confounders and deviations

The server serializes generation, so a complete metric after the stop boundary
is evidence that the active generation returned. This is not a general
concurrent-request correlation protocol. A metric emitted just before the
stop snapshot can conservatively cause an abort; no next task is admitted on
that uncertainty. A one-task diagnostic does not repeat the eight-task
isolation experiment.

## Evidence

`/Users/chad/Models/agentwing/evidence/AW-0014/20260904T203854Z`.
All seven archived file checksums pass. Summary SHA-256:
`dfc6acfd5841ed6965639dd4ffddd1bc029838a4ad3b93865a311a7011d52cc6`.

## Conclusion

The stricter metric barrier works on the real cancellation path and rejects
the tested misleading log fixtures. The next full-suite experiment inherits
fail-closed behavior if a future timeout cannot establish its terminal metric.

## Disposition

Promoted as runner integrity infrastructure, not as a performance improvement.
