# AW-0106 — Capture complete real flash-attention bindings

## Status and hypothesis

Complete capture pass. Frozen plan: retrieve Q/K/V/mask/output for real full
attention layers3/31/63, explicit FP32/FP16 strides,15 complete files, native0,
128MiB aggregate/32MiB per-view cap,120s and existing host gates. Native callback
asks only FLASH_ATTN_EXT whose K view ancestry identifies cache_k_l3/31/63.
This avoids assuming a node name on an unnamed fused flash-attention operator.

## Results and limitations

All15 captures collected. Q256x16x24, K/V256x256x4, output256x24x16, mask256x16.
Real GQA24/4=6. Noncontiguous Q/K/V axes retained with exact byte strides.
Cache has256 padded positions, only16 populated/causally available here;
mask -inf and inactive cells are not blanket finite-value assertions or
quantization inputs. Source capture is not decoder/attention fidelity proof.
Pressure monitored during inference peak1/swap growth0, all children stopped.

First launch preparation failed because header receipt was omitted; no plan
written and no inference started. Copied unchanged pinned header receipt and
reran the same source/parameters; failure sidecar preserved. No trace reset.

## Configuration and provenance

16GB M1 Macmini9,1/internal SSD/macOS27.0.1 build26A434; Prism native runtime
adfffbe41b2cabcd51fff326ab045662265062bb. Original PTQ model HF revision
b072e1d3b35a0a630cece372c2127528e0994386, SHA
53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3.
Raw iterator prompt,16 tokens, context2048, batch/ubatch128, one sequence,
rollback0 and FP16 K/V; no chat template/sampling/generation/vision or agent
benchmark. Uncontrolled warm page/shader cache, no thermal warning at capture.
No P1/profile/task/verifier/timeout/permission/scoring change. Native build
clang++ -std=c++17 -O2, pinned AW-0093 headers and bundled llama/ggml/base
libraries with absolute rpath. Exact source/binary/library identities in plan.

## Commands and disposition

python3 scripts/capture_bonsai_attention.py (first prelaunch exit1, repaired
receipt-only; actual capture exit0). Source/hash audit passed afterward.
External /Users/chad/Models/agentwing/evidence/AW-0106 includes all raw bindings,
source/headers/binary/runtime/source receipts, failure note, host trace/result
and recursive hashes. Small evidence/AW-0106-real-attention-capture.json.
Retained for CPU oracle and real compressed-cache attention tests; no quality,
speed, Google algorithm equivalence or endpoint promotion.
