# Target

## Objective

Maximize verified autonomous task utility per wall-clock hour on the fixed
local host, subject to host-safety and reproducibility gates.

Agentwing does not require output equivalence with a reference model. It does
require valid tool protocol, enforceable permissions, reproducible execution,
and task outcomes checked by independent verifiers.

## Fixed host

- Machine: Mac mini, identifier Macmini9,1
- SoC: Apple M1
- CPU: 8 cores, 4 performance and 4 efficiency
- Unified memory: 16 GB
- Internal storage class: 512 GB SSD
- OS, firmware, free space, storage path, and thermal state: record per run

An external SSD is a different physical configuration and must not be mixed
with internal-SSD results.

## Baseline B0

- Qwen3.6-35B-A3B 8-bit qpack
- Swiftlet runtime
- Pi agent harness
- One active rollout
- 2 GB expert cache initially
- Context and reasoning policy to be fixed by AW-0001 after pressure testing

## Control C0

- Gemma 4 26B-A4B IT in TurboFieldfare's pinned 4-bit representation
- TurboFieldfare runtime and loopback server
- OpenCode harness
- One active rollout
- Production runtime defaults initially

## Optimization surface

1. Model representation, pruning, and mixed precision
2. Expert placement, caching, storage layout, and I/O scheduling
3. Prefill, reusable prefix state, KV state, and context policy
4. Tool protocol, harness prompt, skills, and recovery policy
5. Speculation, batching, scheduling, and concurrency
6. Task allocation across heterogeneous model configurations

## Non-goals

- Maximizing a model-only academic score
- Preserving exact logits, prose, or reasoning traces
- Reporting isolated kernel throughput as agent performance
- Optimizing for cloud inference economics
- Assuming a larger advertised context is useful on this host

