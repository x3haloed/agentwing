# AW-0010 — Shell-only agent tool profile

## Status

Complete.

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

The strict shell-only arm scored zero but materially reduced inference work.
Its initial prompt was 457 tokens versus 1,450 for the seven-tool control, and
TTFT was 118.0 seconds versus 391.3. Endpoint time was 227 versus 445 seconds.
The first valid shell call listed three files. The continuation reused all 531
prior tokens, prefilling 152 new tokens in 39.7 seconds, then emitted a fully
valid `cat` call followed by an incomplete second `<tool_call>` marker. Strict
parsing rejected the complete generation. Pressure peaked at 1 and swap did
not grow.

## Confounders and deviations

This is a deliberate harness-interface change. Cold latency is not causal
until interleaved replication, but prompt-token count and functional outcome
are valid cheap-screen diagnostics.

## Evidence

Run `20260904T161916Z`: summary SHA-256
`ff2dbf6fef5273e8cfb0a21b36fa2f7355fad2e6a4d87bc251a04ab80cf7dc68`;
transcript SHA-256
`52de24a17d70996219ca1d905acd7dcc943ac2219fed151f2e1f61f9151de8be`.

## Conclusion

The one-tool interface reduced prompt tokens by 68.5% and cold TTFT by 69.8%,
but strict malformed-suffix handling still prevented utility. The tool profile
is worth retaining and combining with an explicit recovery policy.

## Disposition

Retained as a throughput component; rejected as a standalone successful arm.
