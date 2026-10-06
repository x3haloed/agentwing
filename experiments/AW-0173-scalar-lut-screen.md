# AW-0173 — explicit scalar partial-LUT consumer

Freeze same full real17408x5120 matrix/input, F32 partial table and numeric gate,
ABBA complete build/multiply/readback before work. Replace dynamic four-row
accumulator array with four explicit scalar accumulators and constant-index
calls; qh power lookup expressed as selects. Producer unchanged. No weights /
model/precision/tasks/sampler/defaults/runtime changes. Source/binary/model /
input/host/OS/thermal/cache pinned, existing owner/pressure/swap/watchdog gates.

Both candidate outputs finite/relativeL2 1.63418e-6. Complete steady candidate
4.454/4.533ms versus native1.092/1.116ms, about4.1x component cost in both pairs.
Initialization/compiler/allocation/first warmup retained, raw/output/alltiming /
median independent replay passes. Pressure1/no swap growth baseline1135.12MiB.
No endpoint speed or causal register-spill/array conclusion from this test.

Reject explicit-scalar implementation before integration. Application remains
uncompetitive across tested activation-table forms; deprioritize the family
rather than continue incidental variants. Reviewing prior AW91–94 establishes
uniform exact PQ FFN conversion was already slower in single-column screens;
keep those negatives and do not repeat without a materially new hypothesis.
Future work should screen another executable decode form or a measured system
bottleneck while preserving task/reasoning/scoring and frozen P1.

Raw /Users/chad/Models/agentwing/evidence/AW-0173; final manifest
 evidence/AW-0173-scalar-lut-screen.json. P1/default/runtime intact, no promotion.
