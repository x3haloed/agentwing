# AW-0167 — real PTQ full-matrix native Metal reference

Hypothesis: original packed PTQ matrix and captured post-transform input produce
a reproducible native full-row control for activation-LUT comparison. Primary
metric:5120finite output values and exact captured reference agreement. No
candidate/kernel/configuration speedup or endpoint claim.

Freeze directory/tensor/input/source identities before extraction. Original
selective GGUF blk.0.ffn_down.weight type143,dimensions17408x5120,19496960packed
bytes,28B/128weight block. Capture AW1480-turbo token0 input1-0.bin hash verified.
Weights/input staged only outsideGit. Before GPU work, verify complete original
weight/artifact/library profile, source fixture/binary, P1/preflight inputs and
one-owner lock. Full host/OS/thermal/storage/cache/runtime plan pinned before
execution; native original AW137 backend, no model process loaded.

Five native projection compute+readback iterations, first retained warmup.
Initialization/upload outside those inner windows and fixture lifetime charged
separately; no cross-configuration inference from component times. Guarded60s
watchdog, pressure<4/growth<=1024MiB. Exit0,pressure1/growth0 baseline1199.12MiB.
Independent raw/capture hashes and all5120finite F32 values verified, bit-identical
to AW148captured actual model projection. Real scale/layout/control path valid.

Retain reference only. Next actual candidate Metal table construction+application /
readback must be compared interleaved with complete cost and numeric gates,
then real early/middle/late matrices and future candidate-generated activations /
behavior before integration/promotion. P1/default/runtime untouched.

Fixture experiments/fixtures/bonsai-ptq-matrix-control.cpp, compile/run commands
and full metadata/raw weights/input/outputs/logs external
/Users/chad/Models/agentwing/evidence/AW-0167. Small manifest
 evidence/AW-0167-ptq-matrix-control.json. No weights inGit.
