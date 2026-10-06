# AW-0097 — Build and audit exact selective attention GGUF

## Status and hypothesis

Complete integrity pass; runtime unqualified. Frozen plan before build:
convert only64 selected attention-output tensors PTQ143→PQ142, all decoded
ternary codes and raw FP16 scales unchanged, all787 other payloads unchanged,
all metadata/tokenizer/header padding untouched except type/offset fields.
Host pressure<4/swap growth<=1024MiB. Independent LUT verifier must detect
code/scale corruption before build; full on-disk verification required after.

## Configuration

Fixed16GB M1 Macmini9,1/internal SSD/macOS27.0.1 build26A434. HF base revision
b072e1d3b35a0a630cece372c2127528e0994386, original PTQ file SHA
53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3.
Runtime target adfffbe41b2cabcd51fff326ab045662265062bb. Symbolic converter
is the AW-0086 native library; independent verifier embeds pinned Metal LUT
from AW-0079, using staged table lookup rather than converter arithmetic.
All source/helper/compiler hashes in plan/receipt. Native helper compiled
clang++ -std=c++17 -O2 -dynamiclib. License Apache-2.0; original untouched.
No inference/sampling/context/KV/vision/tasks/permissions/scoring changes.

## Results and cost

Built6,041,020,768-byte mixed artifact, SHA
cc11a9c76ee8e94a735e14789e17b952b33c9b84e7fe587b40dfe6cd6b96566c.
Growth94,371,840 bytes (90MiB). All15,728,640 changed blocks verified against
independent LUT during conversion and again from disk; raw scale bits exact.
All unselected payloads copied, hashed and compared from disk. Separate header
and offset audit permits only selected type changes and relocated offsets;
all metadata/tokenizer/remaining header bytes exact. Actual tensor gaps total0.

Warm full build/audit23.286s: source hash3.296s, conversion/write/fsync12.029s,
on-disk code/payload verification3.418s; remaining time includes final artifact
hash and setup. Fsync request0.000447s is not cold-device or physical durable
installation throughput. Conversion chunk1,835,008 source bytes, bounded
buffers; no whole6GB read allocation. Pressure sampled throughout build/audit
by background monitor: peak1, swap growth0. No thermal warning recorded.
Original page cache uncontrolled and warm. This is an unpaired install-cost
observation, not a controlled performance comparison or full runtime memory
claim. Final rename succeeds only after integrity/gates, partial files retained
on failure. Output is outside Git; no source/control artifact replaced.

## Commands and evidence

python3 scripts/build_bonsai_selective_packing.py (exit0).
python3 scripts/audit_bonsai_selective_layout.py (exit0).
External /Users/chad/Models/agentwing/evidence/AW-0097 holds frozen plan,
executed source copies, helper library/compiler receipt, host trace, per-tensor
hashes/result and independent layout audit plus recursive hashes.
Small evidence/AW-0097-selective-artifact-integrity.json contains receipts;
spec/bonsai-selective-packing-artifact.json supplies exact usable artifact path
and identity. The original frozen planned proposal remains unchanged.

## Disposition and limitations

Retained for full working-set loading/compute and candidate-generated
accumulated activations/behavior. Active default and frozen P1 unchanged.
GGUF general.file_type metadata retains original PTQ label intentionally;
tensor types and manifest identify this mixed derivative. No runtime loading,
vision, full memory, full inference cost, general capability or endpoint
improvement has been demonstrated by serialized integrity. Goal remains open.
