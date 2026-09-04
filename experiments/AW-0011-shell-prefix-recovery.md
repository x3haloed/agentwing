# AW-0011 — Shell-only profile with prefix recovery

## Status

Complete.

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

The candidate completed normally in 746 endpoint seconds after seven shell
calls and one observable prefix salvage. It found `RETRY_DELAY_MS=2750`, wrote
`2750` to `ANSWER.txt`, reread the file, and stopped. The original v1 verifier
reported zero solely because the file lacked a trailing newline not required
by the prompt. The corrected v1.1 verifier scores the preserved workspace 1,
equivalent to 4.83 verified utility/hour for this one-task diagnostic.

The run included one failed shell command after Qwen corrupted a long absolute
path, then recovered with a quoted path. Pressure peaked at 1; swap grew 0.88
MiB. A runner telemetry defect originally reported zero failed tools because it
looked for `isError` inside `result`; v1.1 reads the top-level event field.

## Confounders and deviations

This factorial interaction is not an isolated estimate of either component.
Latency remains non-causal until interleaved replication.

## Evidence

Run `20260904T162417Z`: original v1 summary SHA-256
`19b3f3252a98cffe566f87312c5770f44cd1ce4ceb6d617852b1f0370aa415d7`;
transcript SHA-256
`f861290d5867768454c090df6d90ebcb2e42862b38dd71a1587d50d83aa02caa`.
The v1.1 rescore is stored beside the original evidence with SHA-256
`7186f7236f50280ccf9d617e053867ae9a5e603cb1fb6365e7bb0549ca33b5bf`.

## Conclusion

The combined arm passes the semantic cheap gate and establishes the first
nonzero Stage A utility. Its seven calls and corrupted absolute path leave a
large opportunity for a relative-path, action-minimizing shell prompt.

## Disposition

Retained as the first functional Stage A candidate; not promoted or replicated.
