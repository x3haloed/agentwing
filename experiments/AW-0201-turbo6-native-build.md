# AW-0201 — Additive native six-bit cache source and library build

## Status, hypothesis and acceptance

Completed source/build preparation; retained experimental artifact.
Hypothesis: additive100B/128value type can build on stationary runtime base
and expose256dim Q8/F16key vector/matrix attention paths without changing
4bit control. Acceptance predeclared source identity/reconstruction and native
library build only. Actual GPU correctness/cost, behavior and endpoint remain
separate required gates.

## Configuration and commands

Base Prismadfffbe plus archived AW137/AW179/AW182/AW186 stationary series.
Source `/Users/chad/Models/agentwing/runtime-sources/prism-turbo6`, build
`/Users/chad/Models/agentwing/runtime-builds/prism-turbo6`, external evidence
`/Users/chad/Models/agentwing/evidence/AW-0201`. No active profile/default/P1
change. New type147, count148;100byte128group/F16norm/reserved96bytepayload.
AW199 theory64centroid/63cut tables. Binary-search writer/6bit packing,
float-centroid matrix consumer, half-centroid vector consumer, graphinverse.
Cache-keyTurbo6 denied like existingTurbo4; Q8/F16keys permitted for256heads.
No model/task/permission/sampling changes or inference. Fixed16GBM1/internalSSD.

```
python3 scripts/prepare_bonsai_turbo6_runtime.py
# Configure/build commands recorded in evidence receipt.
python3 scripts/check_bonsai_turbo6_cpu.py
```

Preparation refuses existing candidate source/evidence; reproduction requires
fresh paths, pinned base and parent fixtures. Patch can independently apply to
stationary base. Receipt contains complete changed-file/library/raw hashes.

## Results and deviations

13 files changed; archived patch independently reconstructs every changed
file exactly. Release native llama/ggml libraries build successfully.
Both4bit control and6bit CPU codecs match all3layer packed fixtures exactly;
after graph-equivalent inverse, decoded bytes also match:2304 tested groups.
No native Metal runtime compilation/execution yet: embedded source building
is not shader admission. Server/vision executables not yet built.

Initial build rejected invalid generated0f literal. Preserved initial patch,
log and source hashes. Fixed literal generation and C linkage declarations.
Next parity check revealed native4bit CPU dequant contract returns rotated
values while saved fixture includes inverse; corrected new6bit to same native
contract and checker applies inverse to both. Preserved failure explanation
and prior build log. Final CPU parity passes. No experimental gate relaxed.

## Disposition

Retain source/build survivor for native writer row-index, vector/matrix
attention numeric/cost checks on actual layers and both key formats, then
full-model accumulated trajectories/vision/tools/endpoints if those pass.
CPU parity/build do not prove native GPU implementation or performance.
No fullGooglePolarQuant/QJL claim, P1 frozen, full goal remains unproven.
