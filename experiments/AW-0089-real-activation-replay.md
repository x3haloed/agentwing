# AW-0089 — Replay real prompt activations through both native packings

## Status, hypothesis and results

Hypothesis: both exact packing paths reproduce full-model captured PTQ projection
outputs on complete early/middle/late real prompt inputs.
Predeclared limit relative L2<=1e-4 per arm/projection, all finite values,
90s per projection and existing host gates. Deliberate one-token cyclic
misalignment must exceed the limit. Plan frozen before executing each arm.

All 278528 outputs per projection (835584 per arm total) match captured outputs
exactly by floating-point comparison: relative L2 and max absolute error0.
Misalignment gives L2 1.320/1.084/0.492 and is rejected. Pressure peak1, swap0.
Both native Metal formats receive identical actual post-transform src1 inputs;
this covers a16-column prompt matmul path, not single-token generation.

Uses AW-0086 full actual FFN-up weights and exact repacking, AW-0088 real inputs,
untouched pinned native runtime libraries; post-run hashes verified. Controls
remain immutable. No model artifact conversion, accumulated candidate behavior,
vision coverage, speed or endpoint promotion claim. Direct fixed-path calls
make zero agent/tool attempts; no tool accounting endpoint is implied.

## Configuration and evidence

Fixed16GB M1 Macmini9,1, internal SSD, macOS27.0.1 build26A434. No thermal
warning recorded for capture; replay immediately follows on the same host,
with OS page cache and shader cache uncontrolled. No performance claim.
Runtime adfffbe41b2cabcd51fff326ab045662265062bb; model HF revision
b072e1d3b35a0a630cece372c2127528e0994386, model SHA
53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3.
Native builds clang++ -std=c++17 -O2 against pinned headers and bundled dylibs,
absolute runtime rpath; standalone experimental harness/source hashes in plan.
Executed python3 scripts/check_bonsai_activation_replay.py, exit0.
Raw evidence /Users/chad/Models/agentwing/evidence/AW-0089; committed
small evidence/AW-0089-real-activation-replay.json contains result/receipt hashes.
Full source, binary, activation and log hashes in external recursive receipt.

## Disposition

Retained for generated-token accumulation and complete cost screening.
Component fidelity does not establish the requested utility/hour improvement.
