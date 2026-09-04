# AW-0009 — Salvage complete tool-call prefixes

## Status

Complete.

## Hypothesis

When Qwen emits one or more fully valid declared tool calls followed only by
the opening of a malformed additional tool block, executing the maximal valid
prefix will increase Stage A utility without accepting unknown tools, invalid
arguments, inter-call text, or ordinary text after a call.

## Configuration identities

- Control: strict B0 Stage A (`AGENTWING_SALVAGE_TOOL_PREFIX=0`).
- Candidate: identical configuration with explicit maximal-prefix salvage
  (`AGENTWING_SALVAGE_TOOL_PREFIX=1`).

## Fixed conditions

- Host, storage, model, cache, sampling, tools, prompt, task, verifier, and
  timeout: identical to AW-0008.
- Runtime candidate: Swiftlet `d7352d7`.
- Task/verifier: frozen Stage A v1.
- Permissions and network: task-local tools, loopback endpoint, offline startup.

## Primary metric and acceptance rule

Primary metric: verified utility per hour. On the cheap falsifier, the
candidate must complete `01-navigation`; all salvages must be observable and
strict parser regression tests must continue to pass. Promotion still requires
the repository-wide replication gates.

## Cheap falsifier

Replay `01-navigation`, where strict B0 executed one valid call and then failed
on a complete valid call followed by a malformed partial call.

## Commands

```sh
cd /Users/chad/Models/agentwing/dependencies/Swiftlet
swift test
swift build -c release --product swiftlet-server

cd /Users/chad/Repos/agentwing
AGENTWING_SALVAGE_TOOL_PREFIX=1 ./scripts/run-aw-0008.sh --task 01-navigation
```

## Results

Swiftlet passes 174 tests across 28 suites and the release server builds.
The candidate scored zero on `01-navigation` and timed out after 910 endpoint
seconds. It executed three valid tools and observably salvaged two malformed
suffixes without a rejected tool output. The first 1,450-token prompt took
384.9 seconds to first token. The first continuation reused all 1,489 prior
tokens and took 6.5 seconds to first token. After truncating history to the
accepted call boundary, the next request matched 1,540 prefix tokens but reused
zero and paid a new 412.3-second prefill. The task read only the development
default and did not reach the production override before timeout. Pressure
peaked at 1 and swap changed by -8 MiB.

## Confounders and deviations

Greedy generation is deterministic for a fixed prompt but OS cache and thermal
state can alter latency. Functional success, not latency, is the cheap gate.

## Evidence

Runtime patch is committed as
`patches/0007-Salvage-complete-tool-call-prefixes.patch`. Candidate run
`20260904T160223Z`: summary SHA-256
`1785b22fbcb560cbb47c9547d67fe868fce3e04a3748e4217c827b5bd505affa`;
transcript SHA-256
`812cd5ec678f691ea84ef9b9a74eb2bcfeb1118e84483e81d51323a8016887aa`.

## Conclusion

Maximal valid-prefix salvage increases the number of productive steps but
does not pass the cheap utility gate. Discarding malformed suffix state breaks
exact live-state reuse; preserving that state would contaminate subsequent
prompt structure. A smaller tool schema is a cleaner next experiment.

## Disposition

Rejected as a performance arm; retained as an explicit off-by-default recovery
prototype.
