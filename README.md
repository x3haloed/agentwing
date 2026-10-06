# Agentwing

Agentwing maximizes verified autonomous coding work per wall-clock hour on a
16GB M1 Mac mini. **The operational default is Bonsai 2 27B with PrismML
llama.cpp Metal, local vision, and Pi.** Text, vision and real tool loops passed
local admission. Historical P1 (Qwen3.6 8-bit + Swiftlet + Pi) remains a control;
the work-rate results below describe P1, not Bonsai.

| Interleaved pair | Control | Candidate | Verified work-rate gain |
| --- | --- | --- | --- |
| C1 → A1 | 3/8, 1.72 tasks/hour | 8/8, 6.32 tasks/hour | 3.67× |
| C2 → A2 | 3/8, 1.93 tasks/hour | 8/8, 6.35 tasks/hour | 3.28× |

Both candidate runs stayed at memory-pressure level 1 with zero swap growth.
The frozen eight-task suite includes navigation, repair, refactoring, data
transformation, recovery, bounded reads and configuration synchronization.
Failures and endpoint overhead count. These are local Stage A results, not
held-out or external benchmark performance.

## Bonsai 2 migration

The active strategy is now **Bonsai 2 27B + Prism llama.cpp Metal + local vision**.
The initial admission failure is preserved in [AW-0062](experiments/AW-0062-bonsai-local-multimodal.md); corrected admission is recorded in [AW-0063](experiments/AW-0063-bonsai-pi-context-admission.md).
See [Bonsai local inference](docs/BONSAI_LOCAL.md) for the guarded chat/image server,
Pi configuration, artifact pins and managed workspace-copy launcher. Historical
P1 measurements below remain measurements of Qwen/Swiftlet/Pi.

## Use the historical P1 local agent

From this repository:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_local_agent.py --check-only
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_local_agent.py \
  --workspace /absolute/path/to/project \
  --task-file /absolute/path/to/task.txt
```

The agent works in a preserved copy under the printed `run_dir/workspace`.
Review its changes and run your tests before applying them to your project.
The launcher manages the loopback model server, private Pi state, a 900-second
task deadline, memory limits, and process cleanup. User-task completion is not
a correctness score. See [the usage and reproduction guide](docs/LOCAL_AGENT.md)
for exact settings, output files, permissions, and benchmark commands.

## What changed

P1 permits repeated code tokens, retains complete tool-call boundaries for
continuation reuse, and uses a 512-token output budget with a compact bash
prompt. The improvement is measured for this complete system; individual
settings do not inherit the combined speedup claim.

The model/runtime/harness identities, prompt, recovery policy and permissions
are pinned in [the P1 profile](spec/validated-local-agent.json). The historical
B0/C0/K0 definitions in `spec/configurations.json` remain unchanged to preserve
the frozen execution plan; P1 is the historical promoted task-launch profile; the Bonsai profile has separate admission and usage documentation.

The final launcher smoke passed independent artifact verification. Validation
includes 180 Swift tests across 29 suites, 19 Python tests, real Pi protocol
fixtures and inherited write/network-boundary canaries. Runtime source was
reconstructed from nine archived patches and independently built and tested.
The clean build differs in executable bytes; the measured original binary
remains pinned. This establishes source/build reproduction, not bit-identical
compilation or performance equivalence of a replacement binary.

## Evidence and follow-up work

- [Promotion report](docs/PROMOTION_REPORT.md): requirement audit, results,
  failures, scope and stopping condition.
- [AW-0027 comparison](experiments/AW-0027-interleaved-promotion-comparison.md):
  all four runs and the declared observer-only audit amendment.
- [AW-0028 handoff](experiments/AW-0028-local-agent-handoff.md): launcher checks,
  failed setup/cleanup trials, fixes and real-model smokes.
- [Learnings](LEARNINGS.md): retained, rejected and deferred experiments.
- [KV accounting](docs/KV_MEMORY.md): why quantized KV remains a long-context
  follow-up rather than part of P1.
- [Validation protocol](docs/VALIDATION_PROTOCOL.md): frozen local acceptance
  contract and the separately scoped broader research roadmap.

Large traces and model artifacts stay under `/Users/chad/Models/agentwing/`;
Git contains source, configurations, compact receipts and hashes. No capacity
cleanup was needed; source, results and provenance were preserved.
