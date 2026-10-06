# AW-0175 — standalone floor arithmetic counterfactual

Hypothesis: unchanged packed-byte floor arithmetic in the standalone AW174
layout approaches native cost, allowing better interpretation of decoder forms.
Predeclared plan/source/fixture pins outside Git before compilation/inference;
primary metric complete compute/readback windows after first retained warmup.
ABBA native/standalone/standalone/native, five iterations per fresh process.
Same real17408x5120 layer0 FFN-down matrix and captured early activation from
AW167; original PTQ28-byte blocks and half scales, no precision/model change.
Replace only static weight coefficient lookup with floor arithmetic in AW174
prototype; remove decoder constant. No activation LUT/producer/workspace.

Native steady1.097/1.119ms; standalone1.243/1.275ms (1.133/1.140x).
Finite5120 outputs, relativeL2 3.86541e-7, identical output hash to AW174.
All exits0, independent raw/output/log-timing/median replay passes; pressure1,
swap growth0, baseline1135.12MiB. Full source/runtime/model/host/OS/thermal/cache
pins in execution plan and committed receipt. Compile/startup/allocation and
first warmup retained; component windows do not represent endpoint utility.

Standalone floor overhead is substantially smaller than AW174 table overhead,
but different runs and native dispatcher/library tuning still confound precise
causal attribution. Retain diagnostic; fixed-table implementation remains
rejected. No runtime/profile/P1/task/sampling/vision changes or promotion.
Next viable decoder design should be screened inside native execution layout
rather than expanding standalone table variants without evidence.

Reproduce: swiftc -O experiments/fixtures/bonsai-standalone-floor.swift -o
external candidate; frozen plan then python3 scripts/run_bonsai_standalone_floor.py.
Runner refuses overwrite of completed summary; retain original raw evidence.
Raw: /Users/chad/Models/agentwing/evidence/AW-0175.
Manifest: evidence/AW-0175-standalone-floor-control.json.
