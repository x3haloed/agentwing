# AW-0170 — exact packed-code partial tables

Before GPU work, freeze CPU/source/input/host/Python/NumPy metadata and original
81activation-block screen/gates. Decompose five-trit byte q into A=(27q)>>8 and
B=((243q)>>8)-9A. Exhaust all256bytes:27-way first-three trits and9-way final-two
trits match independent integer decoder exactly. F32 lookup entries use same
activation precision, weights unchanged. This is not activation quantization.

81real captured block cases across early/middle/late prefixes, own decode points,
three layer FFN-down inputs and block positions pass relativeL2<=1e-4. Max versus
control7.63279e-6 and reference1.04688e-7; wrong lookup code mutation rejected.
864F32values/block,470016B/459KiB scratch at17408, versus3342336B full table.
No native GPU/performance/whole-model claim; actual scales/matrices need GPU gate.
Retain arithmetic survivor only; AW171 separately tests complete Metal cost.
Raw external /Users/chad/Models/agentwing/evidence/AW-0170 and hashes in
 evidence/AW-0170-partial-lut-arithmetic.json. P1/default unchanged.
