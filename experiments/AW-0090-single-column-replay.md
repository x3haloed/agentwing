# AW-0090 — Single-column replay falsifies cross-kernel equality gate

## Status and hypothesis

Terminal negative. Hypothesis: single-column native Metal replay of real prompt
inputs agrees with the captured prompt matmul output under AW-0089's 1e-4
relative L2 threshold. Plan frozen before execution. All finite outputs, same
host gates, 90s per projection. Stop on first failure; later two unattempted.

## Configuration

Fixed16GB M1 Macmini9,1/internal SSD/macOS27.0.1 build26A434, pinned Prism
adfffbe41b2cabcd51fff326ab045662265062bb. Model HF revision
b072e1d3b35a0a630cece372c2127528e0994386, PTQ1_0 SHA
53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3.
First actual prompt-token input column from AW-0088, 5120x17408 full FFN-up
weights/exact PQ representation from AW-0086. Same native replay executable
and libraries as AW-0089, now one column to exercise matrix-vector kernels.
No generation/sampling, vision, endpoint task or permission change. Context
belongs to source capture (2048); isolated replay has no KV/context. Warm page
and shader caches uncontrolled. No timing/performance claim.

## Results

Early PTQ alone differs from captured 16-column prompt matmul by L2
0.0001773824, exceeding predeclared1e-4. Preserve rejection of this comparison
rule; do not raise the threshold after observing failure. Pressure1/swap0.
The script exits0 while recording passed=false: result JSON, not shell exit,
is the authority. Both paths executed before the PTQ comparison rejected.

Post-failure CPU diagnostic on32 evenly spread rows: PTQ error3.8247e-6,
PQ error4.3026e-6 relative to compiled decoder plus math.fsum. All-row
PQ-vs-PTQ L2 6.8865e-6. This indicates disagreement with the prompt-kernel
reference rather than evidence of a PQ-specific error at this sampled layer.
CPU diagnostic is exploratory and does not reverse the predeclared rejection.
Single-column prompt input is not a generated-token activation. No claim about
middle/late layers or accumulated candidate behavior follows.

## Commands and evidence

python3 scripts/check_bonsai_single_column_replay.py (exit0; passed=false).
A separate inline Python/ctypes diagnostic executed with the pinned AW-0082
CPU decoder; its results and hashes preserved. That diagnostic command was not
saved as a standalone executable script; reproducibility therefore also needs
the documented sampled-row dot calculation.
External /Users/chad/Models/agentwing/evidence/AW-0090 contains frozen plan,
inputs/native output/log/host samples/result/CPU diagnostic/recursive hashes.
Small summary evidence/AW-0090-single-column-replay.json pins source and raw
hashes; frozen source and binary checked after execution. No large data in Git.

## Disposition

Reject cross-kernel prompt-output agreement as this decode fidelity authority.
Retain exact packing for a predeclared single-column CPU-oracle experiment,
then generated-token and complete cost/accumulated behavior checks. Goal open.
