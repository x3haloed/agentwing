# AW-0112 — Native Metal inverse WHT

## Status and hypothesis

Retained component. Atomic's unchanged128-group Metal inverse WHT agrees with
its CPU inverse within predeclared .005 relative L2 on every complete actual
populated Q/V collection at Bonsai layers3/31/63. Inverse value-output rotation
is required for the surviving q8-K/Turbo3/4-V path; q8 keys require ordinary Q.

## Configuration and commands

Frozen plan hashes original upstream Metal source/header, extracted unchanged
kernel/sign arrays/argument struct, Swift runner, executable, CPU codec, AW-0109
capture result and executing Python source. No changed kernel arithmetic.
Native Metal compiles extracted source at runtime on Apple M1; Swift runner
uses explicit n_elements/direction args, shared buffers and waits for completed
command.128-element groups, two per256 head. All active values finite; no padding
is treated as data. Source pinned Atomic074bf826e1b06005a51737d29387e36657f41bf7;
model/capture/runtime/sampling provenance inherited frozen AW-0109. No new model
inference, tasks, tools, permissions or generation.
`python3 scripts/check_turbo_metal_inverse_wht.py` exit0.

## Results

Six cases, three layers times Q/V: all pass. Each Q collection6144 values,
V collection49152 values. Maximum relative L2 .000646207; real V cases
.0005993–.0006017. Native kernel uses half4 butterflies versus CPU float;
tolerance declared before dispatch. No thermal/performance claim. Phase pressure1,
swap898.06MiB unchanged, internal SSD M1/16GB/macOS27.0.1/26A434.

## Evidence and limitations

`evidence/AW-0112-metal-wht.json`; raw evidence
`/Users/chad/Models/agentwing/evidence/AW-0112`.
This validates a real GPU bookend on populated captures, not quantized attention
aggregate, complete codec dispatch, compressed-cache accumulated generation,
Google algorithm equivalence or endpoint performance. First harness's missing
forward export is preserved AW-0111. Runtime remains FP16 cache; P1 frozen.
Retain unchanged inverse kernel for subsequent compressed attention execution
checks, with CPU oracle as authority.
