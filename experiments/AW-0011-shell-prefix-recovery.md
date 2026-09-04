# AW-0011 — Shell-only profile with prefix recovery

## Status

In progress.

## Hypothesis

Combining the 457-token shell-only interface with maximal-valid-prefix salvage
will complete `01-navigation` within 900 task seconds because any refill after
recovery is much cheaper than under the seven-tool profile.

## Configuration identities

- Control: strict shell-only AW-0010.
- Candidate: shell-only plus the explicit AW-0009 recovery flag.

## Fixed conditions

- Model, runtime, harness, 0.5 GB cache, task, verifier, sampling, generation
  limit, timeout, host, and storage: unchanged.
- Tool profile: `shell` in both arms.
- Experimental variable: `AGENTWING_SALVAGE_TOOL_PREFIX=1`.

## Primary metric and acceptance rule

Primary metric: verified utility per endpoint hour. The candidate must score 1
on `01-navigation` within the existing timeout, with every salvage observable
and no host-safety violation.

## Cheap falsifier

One run of frozen task `01-navigation`.

## Commands

```sh
AGENTWING_TOOL_PROFILE=shell AGENTWING_SALVAGE_TOOL_PREFIX=1 \
  ./scripts/run-aw-0008.sh --task 01-navigation
```

## Results

Pending.

## Confounders and deviations

This factorial interaction is not an isolated estimate of either component.
Latency remains non-causal until interleaved replication.

## Evidence

Pending.

## Conclusion

Pending.

## Disposition

Unresolved.
