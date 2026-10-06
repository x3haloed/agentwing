# AW-0168 — complete standalone Metal lookup matrix cost

Hypothesis: activation lookup matches real native PTQ matrix within relativeL2
1e-4 and reduces complete construction+multiply+readback cost. Frozen ABBA
control/candidate/candidate/control, five iterations each; first warmup and
process lifetime (including compilation/allocation/upload) retained separately.
Full source/binary/fixture/model/runtime/host/OS/thermal/cache pins in external
plans before GPU execution. One owner, pressure<4/growth<=1024MiB,60s watchdog.

Original17408x5120 full real blk0ffn_down matrix, captured actual early input.
Native control is bit-identical to captured output. Candidate allocates3.1875MiB
lookup, constructs every table each iteration, executes multiply, reads all5120
outputs. Dedicated Metal producer and consumer with explicit buffer barrier.
Weights/scales unchanged, no model/Pi/tool/sampler/task changes or integration.

All outputs finite; candidate relativeL2 1.63420e-6 in both runs. Numeric gate
passes. Steady complete windows: control1.115/1.118ms, candidate7.394/7.404ms.
Both adjacent component pairs about6.6x candidate cost. Process/first warmup
retained; primary inner windows omit initialization but include construction and
readback. No endpoint ratio or extrapolated utility claim. Resource gates pass.
Independent replay verifies all raw hashes/5120outputs/log timings/medians.

Reject initial implementation before integration: assigning each lane a full
block and one output row has costly gathered lookup work. This result does not
reject every LUT layout or prove a particular bottleneck without instrumentation.
Any redesign needs a new frozen screen; no silent reuse of these timings.
P1/default/runtime unchanged, no promotion. Exact sources in fixtures and runner
scripts/run_bonsai_activation_lut_matrix.py. Raw outsideGit:
/Users/chad/Models/agentwing/evidence/AW-0168. Small final manifest:
evidence/AW-0168-metal-lut-matrix-screen.json.
