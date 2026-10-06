# AW-0171 — complete partial-table Metal cost

Frozen independent ABBA, same full17408x5120 matrix/actual captured input and
all5120finite-output relativeL2<=1e-4 numeric gate. AW170 exact 27+9 code split,
F32 table scratch459KiB, row4/eight-lane consumer. Complete table construction /
multiply/readback each iteration; process/compiler/allocation/first warmup retained.
Source/binary/model/runtime/input/host/OS/thermal/cache pins before GPU execution.
One owner, existing pressure/swap/watchdog gates, no task/model/runtime changes.

Both candidate outputs relativeL2 1.63418e-6, numeric pass. Complete steady
candidate4.621/4.812ms versus native1.081/1.125ms, about4.3x candidate cost in
both component pairs. Raw/output/all-timing/median independent replay passes;
pressure1/no swap growth baseline1191.12MiB. Not endpoint utility or a universal
LUT result. Cross-run improvement versus prior variants is not a matched claim.

Reject current partial-table implementation before integration; preserve CPU /
scratch/numeric passes. Instrument actual phase costs before more redesign;
no bottleneck inferred from full windows alone. P1/default/runtime unchanged.
Raw /Users/chad/Models/agentwing/evidence/AW-0171; manifest
 evidence/AW-0171-partial-metal-lut-screen.json. No promotion.
