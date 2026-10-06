# AW-0116 — Native compressed Metal attention

## Status and hypothesis

Retained. Unchanged Atomic q8-K/Turbo3/4-V256/256 vector Metal attention kernels
produce finite real attention outputs agreeing with independent compressed CPU
attention within predeclared relative L2 .005 at full-attention layers3/31/63.

## Configuration and execution

Frozen external plan hashes runner/executable/harness, complete AW-0115 Metal
source, CPU aggregate authority AW-0113, real captured authority AW-0109 and all
prepared input/argument bytes. Original source Atomic074bf826e1b06005a51737d29387e36657f41bf7.
Fixed internal SSD M1 Macmini9,1/16GB/macOS27.0.1/26A434. No new model inference,
sampling, chat effort, tools, task/verifier or permissions changes; capture/model/
Prism runtime identities inherit AW-0109. Candidate trajectory uses FP16 KV.

Four KV heads,24 query heads, dimension256.48 real positions per head, padded
with16 zero-code rows to64; mask0 for real slots and-inf for padding. Actual
Q and packed q8/Turbo buffers retained; independent post-run audit proves
packed data matches AW-0113 authority and padding exactly. Causal final-decode
query sees all48 real positions. Argument fields use native C alignment from
pinned header; immutable field identities/values and bytes in plan.

Function constants: mask true, sinks/bias/softcap/kvpad false, ns10=8/ns20=2,
nsg4/nwg1. Threadgroups1×24×1, threads32×4×1,8192-byte shared scratch.
Unchanged complete Metal source runtime compilation and specialization; command
completion checked. Output remains rotated V domain; inverse bookend validated
separately AW-0113. No selective arithmetic rewrite or scalar GPU substitute.

`python3 scripts/check_turbo_attention_dispatch.py` exit0.90s watchdog and
.25s pressure/swap checks throughout runtime compilation/dispatch; peak1,
swap growth0. No throughput or total-runtime performance claim.

## Results

| Layer | Turbo3 relative L2 | Turbo4 relative L2 |
| --- | ---: | ---: |
| 3 | .00029880 | .00025531 |
| 31 | .00101193 | .00112943 |
| 63 | .00020252 | .00017833 |

All six6144-value complete outputs finite and pass .005 rule. Kernel agreement
is against compressed CPU authority, not original FP16 output equivalence.

## Evidence and disposition

`evidence/AW-0116-native-compressed-attention.json`; raw evidence at
`/Users/chad/Models/agentwing/evidence/AW-0116`. Executed source retained exactly.
Retain actual GPU attention kernels for faithful integration. Missing-inverse
negative remains demonstrated AW-0113; this run adds actual attention dispatch.
No compressed Metal cache writer, Prism registration/actual allocation, complete
compressed generated trajectory, long context, vision, general quality or
endpoint speed acceptance. P1 and currently launched FP16 cache remain intact.
