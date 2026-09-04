# AW-0014 — Require a terminal metric at timeout boundaries

## Status

Implementation complete; model integrity diagnostic pending.

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

Pending.

## Confounders and deviations

The server serializes generation, so a complete metric after the stop boundary
is evidence that the active generation returned. This is not a general
concurrent-request correlation protocol. A metric emitted just before the
stop snapshot can conservatively cause an abort; no next task is admitted on
that uncertainty. A one-task diagnostic does not repeat the eight-task
isolation experiment.

## Evidence

External run manifest and hashes pending.

## Conclusion

Pending.

## Disposition

Unresolved.
