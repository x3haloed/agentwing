# AW-0008 — Freeze compact agentic pre-screen

## Status

In progress.

## Hypothesis

An eight-task deterministic suite can reject non-agent endpoints and expose the
dominant B0 reliability and work-rate bottlenecks before spending the much
larger budget required by the held-out 20-task Stage 2 suite.

## Configuration identities

- Control: pristine task workspaces, which must score zero.
- Candidate: B0 Qwen3.6 + Swiftlet + Pi after the suite and runner are frozen.

## Fixed conditions

- Host and OS: Macmini9,1; exact OS recorded per model run.
- Storage device: internal SSD.
- Model revision and artifact hash: B0 pinned configuration.
- Runtime revision: Swiftlet branch `agentwing/tool-transport`; exact commit per run.
- Harness revision: Pi 0.84.4, pinned by `pnpm-lock.yaml`.
- Adapter revision: exact Agentwing and Swiftlet commits recorded per run.
- Task/verifier revision: `benchmarks/stage-a-v1/manifest.json` and
  `scripts/verify_stage_a.py`; content hashes recorded per run.
- Context and cache: 0.5 GB expert cache initially; exact context telemetry recorded.
- Sampling and reasoning: fixed by the runner before endpoint trials.
- Permissions and network: loopback endpoint; task-local file and shell tools;
  startup network disabled.

## Primary metric and acceptance rule

Primary metric: verified utility per wall-clock hour over all eight tasks.
Report pass count and malformed, failed, redundant, and productive tool calls
beside it. This suite is a pre-screen and cannot promote a default without the
replication and Stage 2 gates in `docs/VALIDATION_PROTOCOL.md`.

## Cheap falsifier

Every pristine workspace must fail and a known solution for every task must
pass the independent verifier.

## Commands

```sh
./scripts/verify-stage-a.sh --self-test
/usr/bin/python3 -m unittest -q tests.test_stage_a_verifier
```

## Results

The pristine-workspace self-test rejects all eight tasks and the positive-path
regression accepts known solutions for all eight.

The first strict B0 falsifier ran `01-navigation` at Agentwing `db060d8` and
Swiftlet `0ac19fe`. It scored 0 utility in 445 endpoint seconds. The first
1,450-token prompt took 391.3 seconds to first token. One `ls` call executed;
the 26-token continuation reused all 1,489 preceding tokens and reached first
token in 6.5 seconds, but its output contained one complete call followed by a
malformed partial call. Strict parsing rejected the generation and the task
never wrote `ANSWER.txt`. Pressure peaked at 1 and swap changed by -8 MiB.

## Confounders and deviations

The suite is deliberately small and locally authored. It measures engineering
iteration speed, not external validity, and must remain separate from Stage 2.

## Evidence

Small deterministic fixtures and verifier live in Git. Model transcripts will
live outside Git under `/Users/chad/Models/agentwing/evidence/AW-0008/`.

- Strict `01-navigation`: `20260904T155047Z`; summary SHA-256
  `1e118e2de1545157ba9b1689a1214aedf56f40b509078dea54cd707574d7562d`;
  transcript SHA-256
  `e41022bfcc464c1c1ee20cddeab6faff758bbf82e8014a2b54410bd4e33b3694`.
- Failed pre-model runner attempt `20260904T155018Z` stopped on an undefined
  metadata variable and produced no model measurement.

## Conclusion

Pending runner completion and first B0 measurement.

## Disposition

Unresolved.
