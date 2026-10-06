# AW-0088 — Bounded native real prompt activation capture

## Status, hypothesis and results

Hypothesis: a selective native callback can capture complete FFN-up inputs and
outputs at layers 0,31,63 without copying unrelated nodes or breaching host gates.
Predeclared plan precedes model execution: exit0, six finite contiguous F32
captures, 64 MiB cap, 120s deadline, pressure<4 and swap growth<=1024 MiB.

The probe passed with 16 prompt tokens, 5120-wide inputs and 17408-wide outputs.
Total captured data 4,325,376 bytes; all tensors contain nonzero values.
Pressure peak1, swap growth0. Full model PTQ1_0 on pinned Metal, no generation.
Callback selects by exact weight name and MUL_MAT operation at the ask phase;
inputs are the operation's actual src1 after preceding transforms, not a guessed
pre-Hadamard activation. Actual backend log records Metal operation execution.

Context2048, batch/ubatch128, one sequence, zero recurrent rollback snapshots,
FP16 KV. Prompt and source/runtime/library/model/header hashes in external plan.
No sampling: prompt decode only. No server/network/tool permission changes.
No vision encoder capture, no candidate accumulation or performance claim.

## Configuration and evidence

Fixed16GB M1 Macmini9,1, internal SSD, macOS27.0.1 build26A434. No thermal
warning recorded for capture; replay immediately follows on the same host,
with OS page cache and shader cache uncontrolled. No performance claim.
Runtime adfffbe41b2cabcd51fff326ab045662265062bb; model HF revision
b072e1d3b35a0a630cece372c2127528e0994386, model SHA
53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3.
Native builds clang++ -std=c++17 -O2 against pinned headers and bundled dylibs,
absolute runtime rpath; standalone experimental harness/source hashes in plan.
Executed python3 scripts/check_bonsai_selective_activation.py, exit0.
Raw evidence /Users/chad/Models/agentwing/evidence/AW-0088; committed
small evidence/AW-0088-selective-activation-capture.json contains result/receipt hashes.
Full source, binary, activation and log hashes in external recursive receipt.

## Disposition

Retained for generated-token accumulation and complete cost screening.
Component fidelity does not establish the requested utility/hour improvement.
