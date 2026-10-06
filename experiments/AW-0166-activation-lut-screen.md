# AW-0166 — activation lookup arithmetic and memory screen

Hypothesis: input-dependent LUT can preserve PTQ block algebra while avoiding
repeated per-output byte decoding. Primary gate: CPU float32 relativeL2<=.0001
against current collapsed-coefficient emulation and independent integer-trit
reference. No Metal throughput or model quality claim.

Frozen before each screen: native shader/source/script/Python/NumPy/host/OS /
thermal/input hashes. Three AW148 accumulated-prefix lengths (0/4096/7695 chunks),
three own decode positions (0/15/31), three layer FFN-down inputs (0/31/63),
first/middle/last128-element block:81cases. Capture hashes independently checked
against source run receipts. Synthetic256 packed blocks cover all256codes in
every byte field; not actual full matrix weights or scales. Unit block scale.

Native decoder has24five-trit bytes plus2four-trit bytes and fp16 scale (28B).
Candidate precomputes24*256 signed dot entries per128-element input block and
leaves qh's eight elements separate. Stored weights unchanged. Largest tested
input17408 needs3342336B (3.1875MiB) table scratch beyond existing input; graph
liveness and all larger model shapes remain unmeasured. Only single vector;
never replicate scratch blindly over prefill columns.

All81CPU cases pass: max candidate/control relativeL2 7.62547e-6, candidate /
integer reference1.07010e-7. This is not native Metal FMA/simd fidelity. V1's weak
additive-output mutation preserved; v2 mutates actual group0 lookup-code index,
which independent decoded reference rejects for every sampled block. Runtime,
weights, tasks, sampler, tools, deadlines, P1 and defaults unchanged.

Retain only tiny arithmetic/scratch survivor. Table construction, allocation,
gathered reads/cache hit rate, complete actual matrix execution, raw real scales
and candidate-generated behavior must pass before full integration. Removing
120 of136 per-block/output floor terms is an operation count, not speed.

Reproduce: python3 scripts/screen_bonsai_activation_lut.py (fresh evidence path
required; frozen plans never overwritten). V1/v2 raw/source/plan/case receipts:
/Users/chad/Models/agentwing/evidence/AW-0166. Small manifest:
evidence/AW-0166-activation-lut-screen.json. No promotion.
