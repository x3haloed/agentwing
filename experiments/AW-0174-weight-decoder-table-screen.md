# AW-0174 — fixed weight-byte coefficient decoder

New hypothesis after activation-table negatives: replace per-output repeated
floor coefficients with a fixed5KiB F32byte-code lookup, leaving no activation
workspace or construction phase. Exact coefficients for all256byte values are
floor(3q/256),floor(9q/256),floor(27q/256),floor(81q/256),floor(243q/256).
Packed weights/scales and original collapsed-coefficient algebra unchanged.

Freeze source/binary/model/full17408x5120 matrix/actual input/host/OS/thermal /
cache identities before same ABBA/numeric<=1e-4/owner/resource/watchdog screen.
One standalone kernel, no additional weight residency or model download;
compute/readback windows retained together with initialization/compile/warmup.

Both outputs finite, relativeL2 3.86541e-7. Complete steady candidate2.533/2.532ms
versus native1.109/1.130ms (~2.3x component cost). Independent allraw/output /
alltiming/median replay valid, pressure1/growth0 baseline1135.12MiB. This rejects
current implementation, not every static decoder form or proves a bottleneck.
No endpoint ratio, new task/scoring/precision/reasoning change or promotion.

Validate comparable standalone unchanged-arithmetic control before further
attribution/redesign; native library dispatcher/tuning can differ from prototype.
P1/runtime/default untouched. Raw external
/Users/chad/Models/agentwing/evidence/AW-0174; manifest
 evidence/AW-0174-weight-decoder-table-screen.json.
