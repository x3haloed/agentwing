# AW-0008 — Freeze compact agentic pre-screen

## Status

First full Stage A floor recorded; replication and broader validation pending.

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

The first candidate completion exposed a verifier defect before a baseline was
declared: task 01 requested only an integer, while v1 silently required a
trailing newline. Stage A v1.1 accepts trimmed text for this task. Inputs and
prompts are unchanged; all future comparisons use the new suite ID and hash.

The first attempted all-task v1.1 run is invalid for baseline scoring. The
runner killed a timeout's wrapper shell but not its descendant Node process.
Orphaned task requests continued into later task windows; task 08's server
segment contains a generation operating on task 05's workspace. The preserved
summary (`20260904T164953Z`) reports 1 utility in 6,931 seconds, but task
isolation and protocol ordering were corrupted, so those aggregate numbers are
diagnostic only.

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
- Invalid all-task v1.1 attempt `20260904T164953Z`: summary SHA-256
  `da9eab85836bfa2fd3446190899b622bf0da4cff01d3aa747644a707d92bc36d`.

## Conclusion

The process-isolated run `20260904T190356Z` completed all eight frozen v1.1
tasks in 5,231 endpoint seconds, scoring 3 utility (**2.064615 utility/hour**).
Tasks 01, 06, and 07 passed; 02, 03, and 04 timed out; 05 and 08 ended without
passing their verifiers. All failures and timeout/cancellation overhead remain
in the denominator. Pressure peaked at 1 and peak/final swap growth was zero.

This run finished before the originating thread was interrupted, but its
result had not reached the project ledger. A takeover audit verified all seven
archived checksums, all eight transcript hashes, tool-event pairing, unique
request ownership, exact partitioning of the server-log suffix into task logs,
unchanged supplied tests, and the three timeout terminal boundaries. Replaying
the frozen verifiers on temporary copies reproduced all eight outcomes.

Every task's initial request reused zero tokens. Five initial requests matched
435 common prefix tokens without reusing them; this is not cross-task state
reuse. The server stayed warm between tasks, and the filesystem cache was not
flushed. Do not label this eight independent cold-start runs.

The first floor used Agentwing `d7714aeca77b4eab0b03ec24e195477527bb17a4`
and Swiftlet `d7352d79ebb13a030bd3eb878510aaed7e9eb5b1`, the compact-shell
prompt, shell-only tools, explicit prefix salvage, 0.5 GB expert cache,
192 output tokens, greedy sampling, and the original 900-second task timeout.
The summary SHA-256 is
`f5d132e241ce2b5027fefa670a521e672c546ef7a9e7cb9c77bd873093d323c4`.
The full run remains at
`/Users/chad/Models/agentwing/evidence/AW-0008/20260904T190356Z`.

Reproduce the offline audit with:

```sh
python3 scripts/audit_stage_a.py \
  /Users/chad/Models/agentwing/evidence/AW-0008/20260904T190356Z
```

The small report is retained in `evidence/AW-0008-first-floor-audit.json`.
Negative controls rejected a foreign-workspace reference, a changed task-log
partition, and valid-JSON transcript tampering. Existing four Python tests and
the eight-pristine-task self-test also passed during takeover.

### Limits and next experiment

This is a local engineering floor, not a promoted default or a general coding
capability score. The suite is small and now inspected for development; keep
Stage 2 held out. Task 06's test covers one normalization example and cannot
support a broader whitespace-normalization claim. Two tasks encountered
rejected tool output; no malformed call was accepted as a successful task.

The runner uses the task as its working directory but does not demonstrate
filesystem or network sandboxing of shell tools. Pi's `--offline` disables
startup network operations only. The audit establishes recorded task-boundary
integrity, not enforceable permission isolation. Thermal snapshots reported
no recorded warning; continuous thermal state, binary hashes, and physical
read accounting remain absent from this run.

Three coding tasks guessed missing `python`/`pytest` commands. Long absolute
paths and repeated incorrect writes added cost, while tasks 05 and 08 exhausted
192 output tokens during rejected generations. These are candidate causes,
not proof that environment guidance or a larger generation budget will improve
utility. Test those variables separately, starting with generic environment
guidance. Do not inject task solutions or change the frozen verifier.

## Disposition

Retained as the first measured Stage A floor. No default promotion.
