# AW-0009 — Salvage complete tool-call prefixes

## Status

In progress.

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
Endpoint result pending.

## Confounders and deviations

Greedy generation is deterministic for a fixed prompt but OS cache and thermal
state can alter latency. Functional success, not latency, is the cheap gate.

## Evidence

Pending endpoint evidence. Runtime patch is committed as
`patches/0007-Salvage-complete-tool-call-prefixes.patch`.

## Conclusion

Pending.

## Disposition

Unresolved.
