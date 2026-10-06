# AW-0169 — eight-lane/four-row LUT cost falsifier

Frozen independent ABBA uses same full17408x5120 matrix, actual captured input,
5120finite-output relativeL2<=1e-4 gate and complete table-build/multiply/readback
windows as AW168. New consumer groups8lanes/block, four shared output rows;
producer/table precision/data unchanged. Original negative implementation kept.
Whole source/binary/model/runtime/input/host/OS/thermal/cache pinning and pressure /
swap/owner/watchdog gates inherited runner, frozen new plan before execution.

Numeric gate passes (relativeL2 1.63411e-6). Complete steady windows candidate
6.307/6.520ms, native1.107/1.131ms, about5.7x candidate cost in both component
pairs. Startup/compile/allocation/first warmup retained. Independent raw hashes,
full output arrays and every logged timing/median replay valid; pressure1/no
swap growth baseline1191.12MiB. No endpoint or universal LUT speed claim.

Reject this full256-entry F32table form before runtime integration. Reduced row
layout does not resolve observed cost; bottleneck cannot be attributed without
instrumentation. Next screen partial-code tables with unchanged arithmetic /
precision to reduce table footprint before any further GPU work. P1/default /
runtime unchanged. Raw external /Users/chad/Models/agentwing/evidence/AW-0169,
final manifest evidence/AW-0169-row4-lut-screen.json. No promotion.
