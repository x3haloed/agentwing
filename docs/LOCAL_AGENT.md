# Local agent P1

P1 is the promoted Qwen3.6 + patched Swiftlet + Pi configuration for this
16GB M1 Mac mini. Both interleaved Stage A comparisons passed. The final task-launcher
real-model smoke also passed independent artifact verification and cleanup.

## Run a task

From `/Users/chad/Repos/agentwing`, check the installed inputs and host:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_local_agent.py --check-only
```

Put the task instructions in a text file, then run:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_local_agent.py \
  --workspace /absolute/path/to/project \
  --task-file /absolute/path/to/task.txt
```

The launcher prints `run_dir` under `/Users/chad/Models/agentwing/tasks/`.
It works in `run_dir/workspace`, a copy of the supplied project, and preserves
the original. Review the changes there and run the project's tests before
applying them to the original. The copy includes hidden files and preserves
symlinks; external symlink targets remain outside the writable boundary. Use a
focused project directory: copying large dependency/build directories costs
time and disk space. No generated work is automatically merged or published.

Each run contains the task, profile manifest, prompt/models, `server.log`,
`pi.jsonl`, `pi.stderr`, `pressure.tsv`, `result.json`, hashes, workspace and
private Pi state. `client-completed` means Pi exited successfully without a
reported model-error event. It is not independent verification of correctness;
user tasks have no benchmark utility assigned. Ctrl-C stops the owned Pi and
server process groups and preserves the run. Normal completion also stops both.

P1 permits workspace/private-state writes and outbound requests to the local
endpoint. Other reads and OS capabilities remain allowed; this is a scoped
write/network policy, not a comprehensive hostile-code sandbox. Package
installation from the network is unavailable inside the task. The model server
listens on `127.0.0.1:8080`; another listener or known model owner blocks launch.
The launcher samples pressure/swap every second during the task, stops at
pressure>=4 or swap growth>1GiB, and enforces a 900-second task deadline.
Its single-instance lock covers this launcher. Run no other model workload
alongside it. Evidence and workspace copies are retained; no automatic cleanup
removes them.

## Exact configuration

Machine-readable settings are in `spec/validated-local-agent.json`. The profile
and prompt files are byte-identical to AW-0027 A2. Do not use the generic
`config/pi-models.json` or `scripts/pi.sh` as substitutes for this launch path.

- Qwen3.6-35B-A3B 8-bit qpack revision
  `720a56073578a3b42b5c40410baf90281bab9c0f`; all 50 payload hashes checked.
- Swiftlet revision `459b2011375022a6716463bd1e1f1b00741f91c3`, original release
  binary SHA256 `5223ce7bd0fb92c0cf5c2adddf54a9b30b971e3bcf7dd25ac62ea5e7ec2cf4ff`.
- Pi 0.84.4, source `6aedd1066e540642165aa30fa7b4a1b863778aa7`; Node path and
  package/runtime hashes are pinned by the frozen plan.
- Expert cache0.5GB, one rollout, bash tool, compact-shell prompt, thinking off.
- Maximum512 output tokens; temperature0, presence penalty0, frequency
  penalty0.5, no-repeat-ngram0, min-new-tokens8, top-k20, top-p0.8.
- Schema-tag normalization and complete-prefix salvage are declared; generation
  stops after retaining and consuming `</tool_call>`. This preserves exact
  continuation reuse. Both candidate replications had zero salvage/rejections.
- Fresh per-task state; identical scoped write/network boundary in both arms.
  The declared262144 context window is metadata, not validated local capacity.

The profile fixes observed code-generation failures from the hard trigram ban
and short output budget while retaining complete tool-call boundaries. The
paired results support this combined system; they do not isolate each change's
causal contribution. Raw-history replay still sometimes refills older context.
No optional output-cap, relative-cwd or history extension is loaded.

## Reproduce the benchmark

The eight tasks, verifiers,900-second timeouts and original execution scripts
remain frozen. The following checks inputs without loading a model:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_frozen_arm.py \
  evidence/AW-0027-frozen-plan-v2.json A2 --check-only
```

To repeat the candidate full suite, omit `--check-only`. It writes a new dated
run, not an overwrite. For a complete new interleaved comparison, run slots
`C1`, `A1`, `C2`, `A2` sequentially and await each process exit before the next.
The tool does not enforce slot order; the recorded four launches do. Keep the
same host/storage and original binary. A new run is new evidence and does not
replace the archived AW-0027 results.

Audit terminal runs and compare each pair with:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/audit_stage_a.py /absolute/run/path
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/assess_stage_a_pair.py /absolute/control/run /absolute/candidate/run
```

AW-0027 used C1`20260905T010110Z`, A1`20260905T024837Z`,
C2`20260905T040519Z`, A2`20260905T053919Z`, all under
`/Users/chad/Models/agentwing/evidence/AW-0027/`. Pair reports, independent audits,
launch receipts and the four-launch identity/order check are committed in
`evidence/`. Plan v2 explicitly fixes an offline terminal-log predicate; no
measured execution input or scoring was changed between arms. The original
observer failure and plan remain preserved.

## Reproduce runtime and protocol validation

`spec/dependencies.json` pins upstream, nine patches, exact source tree, model
and Pi. Verify reconstruction with:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/verify_runtime_patch_series.py
```

AW-0026 cloned the local Swiftlet source without hardlinks into an independent
checkout, detached at the pinned revision, and ran:

```sh
swift build -c release --jobs 2 --disable-automatic-resolution
swift test --jobs 2 --disable-automatic-resolution
```

It passed180 tests across29 suites with a clean tracked tree. Compiler/OS,
resolved dependency hash and raw logs are retained in AW-0026. The clean binary
has different bytes, so this is source/build reproduction, not bit-identical
compilation or demonstrated performance equivalence of that binary. The
launcher deliberately rejects a substituted binary until separately validated.

For protocol/lifecycle checks, while no model is running:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 tests/probe_local_agent_protocol.py
```

The protocol probe uses real Pi and a synthetic loopback server; it checks five
tool results, an expected failed command, recovery and the output artifact.
The original AW-0024 inherited-write/network canaries and Pi fixtures also
remain part of the promotion evidence.
