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
- `spec/configurations.json` — locked B0 and C0 definitions

## Status

Repository scaffolded. No model has been downloaded and no endpoint result has
been claimed. Disk space currently occupied by Firewing must be released or a
separate storage condition must be declared before model installation.

