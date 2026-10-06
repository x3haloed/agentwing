# AW-0185 — actual norm-corrected V codebook screen

Hypothesis: AW184 stationary16level table reduces actual V and attention error
with identical128group/68byte4bit layout, normcorrection and WHT. Freeze actual
layers3/31/63 own32 captured AW109 inputs and table derived without task data.
Gate: baseline packedencoder bitexact native, finite complete decodedvectors,
both candidate V/attentionL2 lower eachlayer; reject any layer regression.
No model loaded, sampling/task/vision/tool or performance comparison.

First helper link failed (private static forwardWHT), runnerdlopen failed before
plan/numeric trial. Failedsource/error preserved. Copy unchanged source signs /
forwardWHT into standalone helper; public inverse and half conversion stay in
pinned native lib. Native packedbyte parity passes every captured group.

Actual V relativeL2 native→candidate: layer3 .135841→.096730,
31 .129946→.094941,63 .127827→.094209. AttentionL2 .078508→.051720,
.088857→.070238,.092641→.055247: reductions34.1%,21.0%,40.4%.
Samebitcount/sameformat/normcorrection; all3gate pass. Independent scalar
math.fsum score/softmax/value attention replay and hashes/numeric errors pass.
Hostphase pressure1/no growth. InternalSSD16GBM1; OS/hardware/source/library /
modelcapture/codebookauthorities in plan. Large inputs/decodedvectors outsideGit.

Retain CPU mathematical/actual-vector survivor, not whole-model or Metal cost
acceptance. Candidate table changes cache encoding semantics; old runtime
stays frozen, no deployedprofile change. Next isolated GPU writer/decode and
block/vector attention early/mid/late cost/integrity before own generated
accumulated trajectories and full multimodal/tools/endpoints. No promotion.

Command: compile bonsai-codebook-codec.cpp to externalcodec.dylib against AW182
libggml-base; python3 scripts/screen_bonsai_actual_codebook.py (refusesoldplan).
Raw: /Users/chad/Models/agentwing/evidence/AW-0185.
Manifest: evidence/AW-0185-actual-codebook-screen.json. P1/default unchanged.
