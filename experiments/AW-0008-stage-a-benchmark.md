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

The pristine-workspace self-test rejects all eight tasks. Positive-path
regression results pending.

## Confounders and deviations

The suite is deliberately small and locally authored. It measures engineering
iteration speed, not external validity, and must remain separate from Stage 2.

## Evidence

Small deterministic fixtures and verifier live in Git. Model transcripts will
live outside Git under `/Users/chad/Models/agentwing/evidence/AW-0008/`.

## Conclusion

Pending runner completion and first B0 measurement.

## Disposition

Unresolved.
