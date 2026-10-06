# AW-0082 — Compiled exact repacking reference

## Status and hypothesis

Passed tiny compiled CPU reference falsifier. An exact symbolic PTQ1_0 to
PQ2_0 layout conversion preserves CPU dequantized FP32 values and raw scale.
This extends AW-0081 integer source mapping; no full model acceptance implied.

## Configuration identities and fixed conditions

Pinned Prism source `adfffbe41b2cabcd51fff326ab045662265062bb`.
Extracted exact bodies of both CPU dequantize functions from hashed
`ggml-quants.c`; standalone structures reproduce 28/34-byte layouts. Half
conversion uses native __fp16 via memcpy; this wrapper is not full runtime
linkage. No model weights read or candidate runtime launched. Exclusive
model-owner lock and post-run preflight passed; AW-0080 was already terminal.
Compiler is Apple clang 21.0.0; actual full version and OS are in evidence.
No speed or unified-memory measurement made. No sampling, prompt, task,
verifier, cache or thermal claim applies to this codec correctness check.

## Primary metric and cheap falsifier

Require bitwise agreement of 128 FP32 outputs per fixture under compiled
pinned CPU decoder functions with -fno-fast-math. Exhaust every byte value
at each of 26 payload positions plus 128 heterogeneous seeded blocks at
scale 1.0; then all 63488 finite FP16 scale patterns on a heterogeneous
payload, including signed zero/subnormal/negative scales. Exclude NaN/Inf
numeric equivalence; AW-0081 preserves their raw bits only. Deliberately
corrupted PQ2 payload must fail agreement.

## Commands and results

`python3 scripts/check_bonsai_repacking_compiled.py` passed 6784 payload
fixtures, 63488 finite scale patterns and corrupted-code negative check.
Source/compiler command/version/script/generated C/library hashes retained
in `evidence/AW-0082-compiled-reference.json`, SHA-256 `5eaebd5c8069d2d9e29891f980b25cce8935c8a9fdec5dc10abae8171003ad1c`.
External generated source, binary and compiler log:
`/Users/chad/Models/agentwing/evidence/AW-0082/compiled-reference`. No large data or binary committed.

## Confounders, conclusion and disposition

These are extracted CPU functions, not full runtime linkage or compiled
Metal kernels. Real early/middle/late tensors, uncommon activation patterns,
Hadamard metadata, installation cost, residency and accumulated model
behavior remain unverified. Retained for next real-tensor/runtime checks;
not promoted. AW-0080 timeout and other negative results remain preserved.
