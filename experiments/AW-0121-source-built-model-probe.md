# AW-0121 — Source-built model execution baseline

## Status and hypothesis

Retained native runtime baseline. Isolated source-built unmodified Prism runtime
can load the selective Bonsai model, generate32 tokens with native sampler and
produce complete final real attention captures on Metal without host violations.

## Configuration and primary acceptance

Exact source/build identities AW-0120; frozen external plan hashes newly built
runtime dylibs, native probe/source/harness, model and original source-header
receipt. Independent audit verifies compiled source headers match those pins.
Probe derived from AW-0109 with one initialization change: explicit backend
loading from isolated baseline build directory. Linked against source-built
llama/ggml/base with explicit rpath to same directory. No release backend mixing
intended. Native log confirms embedded Metal libraries compile and execute.

Same selective-model SHA cc11a9c76ee8e94a735e14789e17b952b33c9b84e7fe587b40dfe6cd6b96566c,
16-token raw iterator prompt,32 sampled/decoded tokens,seed42,T1/top_p.95/top_k20/
min_p.05/presence0/repetition1,context2048,batch128,FP16 K/V/no rollback sequences.
Raw template, no chat effort claim. One advisory owner lock; no network/tool/task
or permission changes. Internal SSD M1 Macmini9,1/16GB/macOS27.0.1/26A434.

Primary frozen rule: native exit0,15 bounded complete Q/K/V/mask/output captures
at final decode layers3/31/63, host gates.120s watchdog,.25s continuous pressure/
swap samples. Existing admitted runtime/launcher/P1 remain unchanged.

`python3 scripts/capture_bonsai_source_built_attention.py` exit0.

## Results and evidence

All primary gates pass, pressure1/swap growth0, no thermal warning reported.
Independent release comparison: all32 token IDs and final16/32 state identical
to AW-0109; all15 complete capture files and capture index byte-identical.
This also inherits the independently validated CPU attention authority for these
identical bytes. Not a broad behavioral-equivalence claim.

`evidence/AW-0121-source-built-model-probe.json`; raw evidence/native logs,
comparison audit/source copies `/Users/chad/Models/agentwing/evidence/AW-0121`.

## Disposition and limitations

Retain unmodified source-built native baseline for Turbo port comparisons. No
source-built server/vision/agent-harness admission, long-context or endpoint
comparison. Source build hashes remain distinct from publisher release; exact
this-probe agreement does not waive any final acceptance requirements.
