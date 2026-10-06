# AW-0096 — Selective attention paths pass sampled CPU fidelity

## Status and predeclared experiment

Complete pass. Before native execution freeze32 evenly spread CPU-oracle rows
per attention-output projection, both paths L2<=1e-4, deliberate row rotation
must fail,90s per projection and host gates. Actual first prompt-column inputs,
complete6144x5120 weights at linear-attention layer0 and full-attention31/63.
CPU authority is the pinned AW-0082 compiled PTQ decoder plus math.fsum dots.

## Results

All six arm/layer comparisons pass; maximum sampled L2 8.03306e-6 (earlyPQ).
Row misalignment is detected. All complete native outputs finite; pressure1,
swap0. CPU oracle samples32 of5120 rows, not full matrix independently.
No generated-token activation capture, candidate accumulation, vision fidelity
or endpoint quality/performance acceptance follows.

## Configuration and evidence

Fixed16GB M1 Macmini9,1/internal SSD/macOS27.0.1 build26A434; Prism runtime
adfffbe41b2cabcd51fff326ab045662265062bb and model HF revision
b072e1d3b35a0a630cece372c2127528e0994386. Actual AW-0093 inputs, full
AW-0094 exact paired attention-output weights; uncontrolled warm page/shader
cache, no thermal warnings. No generation/sampling/context/KV/vision or agent
tasks in isolated graph. Source capture context2048, FP16 KV, one sequence.
Native source/header/binary/reference/weights/runtime identities in frozen
plans and their linked evidence; no endpoint scoring or permissions changed.

## Commands and disposition

python3 scripts/check_bonsai_attention_cpu_oracle.py (exit0), unchanged pinned
AW-0089 native replay binary. External /Users/chad/Models/agentwing/evidence/
AW-0096, small receipt evidence/AW-0096-attention-cpu-oracle.json. Frozen
source/raw hashes audited; all data outside Git. Retain attention-only option
for full working-set and accumulated behavior tests. Planned selector in
spec/bonsai-selective-packing-candidate.json chooses64 tensors and94,371,840
extra payload bytes (90MiB); artifact not created, active default unchanged.
