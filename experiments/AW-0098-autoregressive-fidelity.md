# AW-0098 — Selective artifact passes bounded autoregressive accumulation

## Status and predeclared experiment

Complete diagnostic pass. Frozen before native execution: interleaved ABBA,
original PTQ control A and exact selective-attention artifact B, fresh full
model/context per arm. Each arm samples its own tokens, no teacher forcing.
Fixed raw iterator prompt, max32/min8 generated tokens, context2048,
batch/ubatch128, one sequence, rollback0, FP16 KV. Sampling T1, top_p.95,
top_k20, min_p.05, repeat1, presence/frequency0, seed42; native chain accepts
sampled tokens. Raw text tokenization has no chat template or reasoning-effort
configuration; this is not a medium-thinking agent run or mode comparison.

Acceptance: pairwise generated token IDs identical; maximum relative L2<=1e-3
on all selected activations and logits; finite values; existing host gates,
180s per arm. Threshold is a cheap accumulated numeric falsifier, not broad
quality authority. Selected capture capped64MiB per arm, logits<=32 vocab rows.
32-token bound limits evidence volume, does not alter endpoint reasoning policy.

## Results

All four arms exit0 and independently generate the same32 IDs. Each captures
198 selected projection nodes (six at prompt plus six per32 single-token
forwards),396 complete input/output tensors and32 full248320-vocab logits rows.
Both interleaved pairs: max activation L2 0.0003502969, logits L2 1.348358e-5.
Independent audit checks every raw file hash, all51,249,152 F32 values across
four arms finite, full shape coverage (prompt16 columns, generation1), and token
trace alignment. This demonstrates bounded candidate-generated accumulation
across early/middle/late attention output and FFN-down; Bonsai is dense, no
expert route selection to validate here. It does not imply uncommon prompts,
longer sequences, vision, tool protocol, or general agentic capability passes.

Pressure peak1/swap growth0 while native processes ran. Only one full model
owner at a time. Candidate logs confirm native PQ2 matvec kernel loaded, full
language-model load and compute succeeded. Runtime libraries and executed
source/binary hashes checked after run. Four native wall observations15.006,
11.060,8.190,15.236s retained, but callback copies/files/hash overhead and warm
shader/page caches make these unsuitable for performance attribution or endpoint
claims. No speed acceptance is drawn from them. Model-integrity hashing before
runtime is not included in native walls; all endpoint overhead remains due.

## Configuration identities

Fixed16GB M1 Macmini9,1/internal SSD/macOS27.0.1 build26A434; pinned Prism
adfffbe41b2cabcd51fff326ab045662265062bb. Base HF revision
b072e1d3b35a0a630cece372c2127528e0994386, PTQ hash
53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3;
selective derivative hash
cc11a9c76ee8e94a735e14789e17b952b33c9b84e7fe587b40dfe6cd6b96566c.
Both Apache-2.0. No vision projector loaded in this text-only diagnostic.
No task/verifier/deadline/tool/permission/scoring change, no held-out exposure,
no modification to original artifact, frozen P1 or active operational profile.
Thermal no warnings at start, caches uncontrolled warm, standalone native
harness revision/source/header/compiler/library identities in frozen plan.

## Commands and evidence

clang++ -std=c++17 -O2, pinned AW-0093 headers, bundled -lllama -lggml
-lggml-base and absolute runtime rpath; exact command/version in compiler.json.
python3 scripts/check_bonsai_autoregressive_fidelity.py (exit0).
python3 scripts/audit_bonsai_autoregressive_trace.py (exit0).
External /Users/chad/Models/agentwing/evidence/AW-0098 contains frozen plan,
executed source copies, helper binary/compiler receipt, all bounded traces,
run/raw hashes, host samples/result and independent audit/recursive receipt.
Small evidence/AW-0098-autoregressive-fidelity.json pins exact receipts.

## Disposition

Retained for full working-set cost, long-sequence/native-chat/vision and
capability evaluation. Not promoted. Serialized and bounded accumulated evidence
now support moving to controlled callback-free runtime and full multimodal
checks; the25% verified utility/hour and preserved capability goal remains open.
