# AW-0010 — Shell-only agent tool profile

## Status

In progress.

## Hypothesis

Exposing only Pi's universal `bash` tool will reduce cold prompt tokens and
tool-syntax failure enough to complete Stage A tasks faster than the seven-tool
profile while retaining the ability to inspect, edit, and validate each task.

## Configuration identities

- Control: strict B0 Stage A seven-tool profile.
- Candidate: strict B0 Stage A with `AGENTWING_TOOL_PROFILE=shell`.

## Fixed conditions

- Model, runtime, harness package, 0.5 GB expert cache, temperature, maximum
  generation, task, verifier, timeout, host, and storage: unchanged from AW-0008.
- Tool prefix salvage: disabled in both arms.
- Candidate action interface: Pi `bash` tool only.
- Permissions and network: task-local working directory, loopback endpoint,
  offline startup.

## Primary metric and acceptance rule

Primary metric: verified utility per endpoint hour. The cheap candidate must
complete `01-navigation` with no rejected model tool output and reduce initial
prompt tokens versus the 1,450-token full-profile control.

## Cheap falsifier

Run the same frozen `01-navigation` task once. Reject the arm if it cannot
produce verified `ANSWER.txt` within 900 task seconds.

## Commands

```sh
AGENTWING_TOOL_PROFILE=shell ./scripts/run-aw-0008.sh --task 01-navigation
```

## Results

Pending.

## Confounders and deviations

This is a deliberate harness-interface change. Cold latency is not causal
until interleaved replication, but prompt-token count and functional outcome
are valid cheap-screen diagnostics.

## Evidence

Pending.

## Conclusion

Pending.

## Disposition

Unresolved.
