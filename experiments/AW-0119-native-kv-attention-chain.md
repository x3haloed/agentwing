# AW-0119 — Both native K/V writers in connected attention path

## Status and hypothesis

Retained. Adding unchanged native q8 key SET_ROWS to AW-0118's native Turbo
value writer→attention→inverse chain preserves correct packed keys and final
attention outputs on actual early/middle/late Bonsai captures.

## Configuration, primary acceptance and execution

Frozen external plan hashes runner/harness/executable, complete Atomic Metal
source, captured authority AW-0109, independent CPU authority AW-0113 and all
prepared input/index/argument bytes. Atomic074bf826e1b06005a51737d29387e36657f41bf7.
Model/Prism runtime/context/sampling identities inherit AW-0109 FP16-generated
trajectory; no new model inference, task/verifier/tools/permissions changes.
Internal SSD M1 Macmini9,1/16GB/macOS27.0.1/26A434.

All actual Q/K/V inputs F32 from populated captures. Native q8 key writer now
uses192 rows,8 blocks/256 dimensions,272-byte row stride, destination indices
head*64+token; no CPU-packed keys consumed in GPU computation. CPU key buffer
is zeroed before command execution and rewritten by GPU. Turbo3/4 V writer
and attention/inverse settings inherit AW-0118. Four ordered encoders in one
command buffer per case, with GPU buffers retained between stages.

Primary unchanged rule: each full final output finite and relative L2<=.005
against independent compressed CPU inverse aggregate.90s watchdog/.25s host
checks throughout runtime compilation/dispatch. Key bytes and final-output
identity are additional diagnostics, not a replacement for CPU acceptance.
`python3 scripts/check_turbo_kv_attention_chain.py` exit0.

## Results

All six6144-value outputs pass, max relative L2 .00129833 against CPU authority.
Every actual GPU-written q8 key buffer equals CPU authority, including zero
masked padding. Every GPU-written V buffer and restored output equals AW-0118
byte for byte. This rules out an unnoticed key-writer layout change in these
cases. Peak pressure1/swap growth0; no performance claim.

## Evidence and disposition

`evidence/AW-0119-native-kv-chain.json`; raw evidence
`/Users/chad/Models/agentwing/evidence/AW-0119`. Retain complete standalone
GPU K/V-write→compressed attention→inverse path for Prism integration.
Actual Prism cache type registration/allocation, generation under compressed
cache, longer contexts/rare patterns, vision and replicated end-to-end acceptance
remain outstanding. P1/current FP16 runtime unchanged.
