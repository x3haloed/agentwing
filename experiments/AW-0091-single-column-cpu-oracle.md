# AW-0091 — Single-column real inputs pass independent CPU oracle

## Status and hypothesis

Complete pass. Before execution, freeze relative L2<=1e-4 for both native
packing paths against compiled CPU decoder plus math.fsum on32 evenly spread
rows of each early/middle/late projection. Rotating row correspondence must
fail. This new authority does not reverse AW-0090's cross-kernel rejection.

## Results

Both paths pass layers0/31/63: maximum sampled L2 5.82305e-6. Deliberate
misalignment L2 1.54/1.31/1.40 fails. Pressure1/swap0. All complete native
outputs finite; CPU oracle samples32 rows per17408-row projection. This uses
actual first prompt-token inputs and single-column matvec kernels, not
captured generated-token activations or accumulated candidate behavior.

## Configuration and evidence

Fixed16GB M1/internal SSD/macOS27.0.1 build26A434, native pinned Prism runtime
adfffbe41b2cabcd51fff326ab045662265062bb. Model HF revision
b072e1d3b35a0a630cece372c2127528e0994386; AW-0086 exact full5120x17408
FFN-up weights, AW-0088 actual inputs, AW-0082 compiled decoder. Frozen
plan pins all source/binary/reference/weight/capture hashes. No sampling,
vision or endpoint tasks; replay has no context/KV and source capture uses2048.
Caches uncontrolled, no timing claim. No tools or permissions changed.
Executed python3 scripts/check_bonsai_single_column_cpu_oracle.py (exit0).
Raw external /Users/chad/Models/agentwing/evidence/AW-0091 and committed
small evidence/AW-0091-single-column-cpu-oracle.json preserve raw/source hashes.

## Disposition

Retained for complete cost and generated-token/accumulated behavior checks.
No utility/hour or broad capability claim.
