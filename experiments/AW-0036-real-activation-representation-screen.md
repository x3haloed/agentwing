# AW-0036 — Real activation authority for executable expert recoding

Status: capture design, not implemented or measured.

Question: can a smaller executable expert representation preserve representative
P1 routed-mixture behavior while offering a credible complete-path cost reduction?
AW-0033 excludes assuming half-sized storage alone delivers 25% utility improvement.
AW-0031/32 establish substantial disk demand and limited simple transport gains.

First required artifact: bounded real input activations, selected expert IDs and
routing weights from P1 at early/middle/late layers. Use new public diagnostic
prompts unrelated to held-out tasks; do not use the sealed panel as calibration.
Capture both prompt processing and decode. Match original greedy output and routes
with capture disabled/enabled, and archive source/binary/input identities.

Source inspection at isolated Swiftlet-AW0031 (406f992) identifies:
- legacy moeForward receives the CPU x array at the routing callback;
- fast decode has synchronized GPU output before routerPicks and reads expert
  input from readSlot(slot, reg.xmoe, hiddenSize);
- layer-major prefill has synchronized output before per-token routerPicks and
  uses prefillSlot(t) for the same expert input region;
- selected picks and normalized weights are separate in the fast paths. Preserve
  their actual order and values; do not recompute from rounded logged logits.

Capture only selected layers and bounded positions, with explicit phase/position
metadata and finite-value checks. Instrument an isolated checkout; do not rebuild
or replace P1's original runtime. Build/capture waits for the active AW-0035 model
run to end, preserving one model owner and uncontended physical measurements.

After capture, establish original 8-bit projection/mixture authority using the
same GPU arithmetic before evaluating recoding error. Existing runtime has direct
four- and eight-bit affine GEMV paths, which may reduce executable memory traffic
as well as storage, but their presence proves neither candidate fidelity nor speed.
Do not port Prismwing/Firewing error thresholds blindly. Freeze diagnostic screens
before candidate measurements; end-to-end task preservation remains authoritative.

This design does not justify a full bank conversion, kernel promotion or fidelity
claim. Candidate-generated accumulated routes/activations and held-out behavior
remain required after source-activation screening.
