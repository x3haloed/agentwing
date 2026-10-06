# AW-0093 — Capture real attention-output and FFN-down inputs

## Status, hypothesis and result

Complete pass. Frozen plan: selective native callback must capture exactly six
complete input/output pairs, finite contiguous F32, <=64MiB, <=120s and host
pressure/swap gates. Select early/middle/late FFN-down and attention output.
Early layer is linear attention: its actual weight is blk.0.ssm_out.weight;
middle/late use blk.31/63.attn_output.weight. Selection follows actual pinned
model directory, not an invented uniform architecture.

All six pairs captured across16 prompt-token columns. Attention input6144,
FFN-down input17408, outputs5120. Pressure1/swap0. Callback asks only for
selected MUL_MAT nodes and collects actual src1 after transforms. Full native
PTQ prompt inference, context2048, batch/ubatch128, one sequence, rollback0,
FP16 KV. Same small iterator prompt as AW-0088; no generation/sampling/vision.

## Fixed configuration and provenance

16GB M1 Macmini9,1, internal SSD, macOS27.0.1 build26A434. Runtime Prism
adfffbe41b2cabcd51fff326ab045662265062bb; model HF revision
b072e1d3b35a0a630cece372c2127528e0994386, PTQ1_0 SHA
53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3.
Uncontrolled warm OS page/shader cache; no thermal warning observed. Exact
source/model/header/native binary/runtime dylib pins in external frozen plans.
Native build clang++ -std=c++17 -O2 with pinned headers, bundled dylibs and
absolute rpath. Neither P1 nor task/verifier/reasoning/timeout/permissions/scoring
was changed. No agent endpoint utility or general capability claim.

## Commands, evidence and disposition

python3 scripts/check_bonsai_operation_activation.py (exit0).
External /Users/chad/Models/agentwing/evidence/AW-0093; small committed receipt
at evidence/AW-0093-other-operation-activations.json. Frozen source/runtime
hashes rechecked after execution; all raw files have recursive receipt hashes.
Retained for operation replay, cost and generated-token accumulation. Complete
capture alone does not prove PQ fidelity or accumulated candidate behavior.
