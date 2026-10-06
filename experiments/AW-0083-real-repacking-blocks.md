# AW-0083 — Real serialized tensor repacking screen

## Status and hypothesis

Passed bounded real-block CPU fidelity screen. Exact symbolic repacking
preserves compiled CPU decoder output for sampled installed PTQ1_0 blocks.

## Identities and fixed conditions

Model revision `b072e1d3b35a0a630cece372c2127528e0994386`, installed language artifact SHA-256
`53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3` verified in full before bounded payload reads.
Runtime source adfffbe and compiled reference library pinned by AW-0082.
Exclusive model-owner lock and preflight; no concurrent inference. Internal
SSD on fixed M1 host. No model runtime, prompt, sampler or task used; no
performance or memory-residency claim. GGUF directory parser is copied into
a new helper; old frozen inspector and all active profiles remain unchanged.

## Primary metric and cheap falsifier

Bit-identical 128 FP32 values from compiled reference decoders for five
positions (first, quarter, middle, three-quarter, last block) in every PTQ
serialized tensor. Reject nonfinite scales or mismatches. These are real
weights, not real routed mixtures or accumulated activations. Bonsai directory
has no expert-named tensors; MoE routing ladders do not transfer directly.

## Commands and results

`python3 scripts/check_bonsai_repacking_real_blocks.py` passed 2010 blocks from
all 402 PTQ tensors, reading 56,280 payload bytes after full artifact hash.
Includes early/middle/late layers and output head. Exact full packing expansion
from installed tensor shapes is 1,259,520,000 bytes, matching published artifact
size difference. This measures logical file expansion, not actual installation
writes, physical reads, residency or runtime speed.

## Evidence and limitations

`evidence/AW-0083-real-blocks.json`, SHA-256 `b9ec01de7f0811b598085ddf06fd58a5f87ba93f9b086d0664159a1df061e1eb`, pins both executed/current
probe source, library and directory reader. Per-block offsets/hashes and raw
model blocks remain outside Git at `/Users/chad/Models/agentwing/evidence/AW-0083/real-blocks`.
Output-only postprocessing relocated the large sample manifest outside Git;
executed source reconstructed byte-for-byte and hash-verified there. Current
script incorporates the same relocation; sampling/codec logic unchanged.
No full tensor, model artifact, Hadamard metadata conversion, Metal invocation,
activation mixture or candidate accumulated behavior validated yet.

## Disposition

Retained for full streaming tensor equivalence and runtime fidelity checks.
Not promoted; AW-0080 failure and all broader/endpoint gates remain preserved.
