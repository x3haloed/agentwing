# AW-0085 — Independent CPU oracle for tiny Metal packing

## Status and hypothesis

Passed independent component oracle. Both native Metal packing paths match
CPU-decoded weights and a separate high-precision dot calculation within the
predeclared tiny-component tolerance. This strengthens AW-0084, which only
compared formats to each other and could miss shared error.

## Identities and fixed conditions

Unchanged AW-0084 native library/header hashes verified before execution;
AW-0082 compiled CPU decoder library verified. Both use pinned Prism commit
adfffbe41b2cabcd51fff326ab045662265062bb. Original AW-0084 fixture receipt
verified, from AW-0083 pinned real model samples. Matrix remains rearranged
64 sampled blocks by 128 codes with four synthetic input patterns, not a real
full projection or activation. Native fixture writes the actual input and
both output arrays for independent calculation. New source preserves AW-0084
source and evidence. Exclusive model owner/preflight and 60s subprocess
limit; no full model inference. No timing, host-pressure or endpoint claim.

## Primary metric and cheap falsifier

For each arm require finite 256 outputs and relative L2 <=1e-4 against
compiled CPU PTQ dequantization followed by Python math.fsum of double
products of actual recorded FP32 inputs. This provisional numerical component
falsifier is not broad model fidelity authority. Rotating oracle rows must
fail to show sensitivity to output ordering/corruption.

## Commands and results

Compile `experiments/fixtures/bonsai-packing-metal-oracle.cpp` with clang++
-std=c++17 -O2 against exact AW-0084 headers and native GGML libraries/rpath.
`python3 scripts/check_bonsai_metal_oracle.py` passes both arms:
PTQ relative L2 1.02138623e-06, PQ relative L2
1.47678762e-06. Rotated-reference relative L2
1.48906639, rejected. Raw input/output
arrays, executable and logs stay outside Git at `/Users/chad/Models/agentwing/evidence/AW-0085`.
Receipt/script/native source hashes:
`evidence/AW-0085-metal-cpu-oracle.json`, SHA-256 `c45fc3a23a45423b3ab6f6564c68798b9001631fed768aadf90730176173ea88`.

## Limitations and disposition

No real full projection shape, captured actual activation, Hadamard application,
candidate accumulated behavior, storage/install/physical-read cost, memory
residency or speed validated. Retain for those next gates, not promoted.
Full Agentwing successor objective and historical negative results preserved.
