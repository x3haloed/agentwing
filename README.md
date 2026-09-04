# Agentwing

Agentwing is a systems-research project for maximizing **verified autonomous
work per wall-clock hour** on one local Apple Silicon machine.

The target is intentionally model-agnostic. Models, quantizations, inference
runtimes, agent harnesses, prompts, caches, speculative paths, and compression
schemes are interchangeable components. A component survives only when the
complete agent system performs more verified work under the host's physical
limits.

## Initial research question

How much raw agentic capability can be embodied in a base M1 Mac mini with
16 GB unified memory, and at what sustained end-to-end work rate?

The primary metric is not token throughput:

```text
verified utility per hour = sum(verifier-weighted task utility) / wall time
```

Decode tokens/s, prefill tokens/s, time to first useful action, productive tool
ratio, peak memory, swap growth, bytes read, and energy are explanatory
measurements.

## Starting configurations

### B0 — capability baseline

- Model: Qwen3.6-35B-A3B, 8-bit qpack
- Runtime: Swiftlet
- Harness: Pi
- Hardware: Macmini9,1, Apple M1, 8 cores, 16 GB unified memory
- Expected model footprint: about 34 GB disk and 7.6 GB peak RAM with a 2 GB
  expert cache
- Published base-M1 decode anchor: about 1.74 tok/s

This is the first model-harness pair to establish, not a claim that it is
already optimal. Swiftlet's Chat Completions server does not yet document
function-tool handling, so an adapter or native tool path is an explicit part
of AW-0001.

### C0 — throughput control

- Model: Gemma 4 26B-A4B IT, TurboFieldfare's pinned 4-bit representation
- Runtime: TurboFieldfare
- Harness: OpenCode
- Expected model footprint: about 14.3 GB disk and roughly 2 GB RAM with 4K KV

TurboFieldfare already documents streaming Chat Completions, function tools,
and single-prefix reuse. C0 tests whether a more complete and faster-serving
system beats B0 on verified work rate despite different model capability.

### K0 — emerging capability candidate

- Model: K2 Horizon MoVA 36B-A4B
- Publisher: Institute of Foundation Models (`IFM`)
- Architecture: 36B stored, about 4B active per token, native 512K context
- Initial artifact: official GGUF repository, exact quantization to be selected
- Harness/runtime: unresolved pending local compatibility and a controlled
  harness screen

K2 Horizon was released on 2026-09-03 and reports 58.6 on Terminal-Bench 2.1
and 26.8 on tau3-Banking, ahead of the Qwen3.6 comparison reported by its
publisher. These are very recent publisher results, so K0 remains an emerging
candidate rather than replacing B0 before independent and local validation.

## Repository map

- `TARGET.md` — machine, objective, and initial configurations
- `RED_LINES.md` — claims and host-safety boundaries
- `LEARNINGS.md` — append-only belief changes
- `docs/ARCHITECTURE.md` — measurement and system boundaries
- `docs/VALIDATION_PROTOCOL.md` — benchmark and acceptance rules
- `docs/WORKFLOW.md` — experiment lifecycle
- `docs/SOURCES.md` — evidence provenance
- `docs/EXPERIMENTS.md` — ordered research program
- `experiments/AW-0001-baseline-bringup.md` — first executable experiment
- `spec/acceptance.json` — machine-readable acceptance gates
- `spec/configurations.json` — candidate definitions, including B0, C0, and K0

## Status

AW-0001 bring-up is active. The pinned 34 GB Qwen3.6 artifact passed all 50
published payload hashes, Swiftlet's 162 tests pass, its release CLI and server
build, and the pinned Pi harness passes a two-turn tool-protocol fixture.

The first real 2 GB-cache smoke produced 1.87 decode tok/s, but system swap grew
from 2.04 GB to 3.66 GB during the 22-second process. Execution stopped at the
pressure boundary. Stock Swiftlet also discards Chat Completions `tools` and
prior `tool_calls`, despite the model template and tokenizer supporting them.
The next work is therefore a measured memory-safe cache arm plus a lossless
Swiftlet tool bridge—not a benchmark score.

## Bring-up commands

```sh
pnpm install --frozen-lockfile --ignore-scripts
./scripts/doctor.sh
./scripts/test-pi-protocol.sh
./scripts/pi.sh --list-models agentwing
```

`scripts/pi.sh` keeps its state under ignored `var/` and does not modify the
operator's normal `~/.pi` configuration. Do not run the real model again until
the swap state and next cache arm have been declared in a new experiment.
