# AW-0109 — Candidate-generated attention capture

## Status and hypothesis

Retained. The selective-attention PQ candidate can produce32 sampled tokens and
expose complete real final-decode Q/K/V/mask/output at full-attention layers3/31/63
without resource-gate violations. This advances beyond prompt-only AW-0106.

## Frozen configuration and primary metric

External `plan.json` freezes source, harness, binary, original Prism runtime
commit adfffbe41b2cabcd51fff326ab045662265062bb, every loaded runtime dylib/header,
and candidate model SHA cc11a9c76ee8e94a735e14789e17b952b33c9b84e7fe587b40dfe6cd6b96566c.
Internal SSD, M1 Macmini9,1/16GB, macOS27.0.1/26A434. Context2048/batch128,
FP16 KV/no rollback sequences, one owner, no network/tool/harness tasks.
Raw iterator prompt from AW-0106:16 tokens;32 generated tokens with native
T1/top_p.95/top_k20/min_p.05/presence0/repetition1/seed42. No chat template or
reasoning-effort claim. Primary acceptance: exit0, exactly15 complete bounded
capture files, three final-decode attention ops, generated32, host gates.

## Commands and results

Compiled native source with Apple Clang and existing pinned AW-0093 public
headers, linking original libllama/ggml/base with explicit local runtime path.
`python3 scripts/capture_bonsai_accumulated_attention.py` exit0. Native log
confirms32 sampled/decoded tokens and initial16.15 capture files retain full
noncontiguous strides. Masks permit48 real keys; padding excluded downstream.
Pressure sampled every.25s, peak1, swap growth0. No thermal warnings reported.
No callback before final generated token, preventing repeated-file overwrites.

## Evidence and limitations

`evidence/AW-0109-accumulated-attention.json` contains external-file hashes and
results. Raw evidence `/Users/chad/Models/agentwing/evidence/AW-0109`.
Generated trajectory is FP16-cache selective representation, not compressed-cache
accumulated behavior. No long-context, rare-route, vision, throughput or endpoint
quality claim. Retain as authority for AW-0110; candidate remains unqualified.
