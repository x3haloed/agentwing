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

## Observer implementation prepared, not built

`probes/activation_capture/ExpertActivationTrace.swift` and
`scripts/prepare_activation_capture.py` now prepare the fast-path observer for a
clean, explicitly named isolated AW-0031 descendant. The original runtime is not
an accepted target. Hooks run after router synchronization, with lazy input reads
only when enabled. Capture layers 0/20/39, first four records per layer/schedule,
at most 24 records. Record position and schedule explicitly; do not equate every
single-token invocation with decode without reconciling prompt length.

Inputs and normalized weights are stored as exact uint32 Float bit patterns.
Dimension, expert IDs/count, finite values and exclusive output-file creation
fail closed. Legacy non-fast execution is intentionally unsupported by this
observer; a real run must prove expected schedule coverage before fixture use.
Build, disabled/enabled output equivalence and actual fixture validation remain
pending until AW-0035 relinquishes the model owner. No capture evidence exists yet.

The prepared supervisor `probe_real_activations.py` uses three public diagnostic
prompts (coding, arithmetic explanation, structured output), each in capture-
disabled/enabled/disabled order with 12 greedy generated tokens and the original
0.5-GB cache. Every arm enables the existing AW-0031 route observer as a common
diagnostic. Acceptance requires identical greedy output and complete route
sequences across each triple. Captured expert IDs must reconcile to layer/position
in the route log; bit patterns must be finite and normalized weights sum to one.
At most 24 captures per prompt are admitted. Each arm has a 180-second deadline
and host gates; failures and raw hashes are preserved. This supervisor is prepared
but not run, and its observer build still needs validation.

## Isolated build and first capture run

Observer source is committed as c3ee0db in
`/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0036`, derived from AW-0031
406f992. Full patch is archived beside this record. Only dependency checkouts,
repositories and workspace-state were copied from the prior isolated build;
no relocated compiled module cache was reused. Release CLI build succeeded in
78.81 seconds using:
`swift build --package-path /Users/chad/Models/agentwing/reproductions/Swiftlet-AW0036 -c release --jobs 2 --disable-automatic-resolution --product swiftlet`.
Build log: `/Users/chad/Models/agentwing/evidence/AW-0036/build.log`.

First capture run launched at
`/Users/chad/Models/agentwing/evidence/AW-0036/20260906T062421.091973Z`.
It follows the declared nine-arm schedule. At launch, no P1 process remained.
Actual capture coverage, route/output equivalence and fixture admission remain
pending until this run completes. P1's source/binary/profile are unchanged.

## Capture admitted

All nine arms exited zero. Exact greedy output and full route sequences match
within each of the three disabled/enabled/disabled triples. All 72 activation
records pass float-bit finiteness, normalized-weight, shape and layer/position
route reconciliation. They contain 576 expert selections covering 250 distinct
(layer, expert) identities at layers 0, 20 and 39. Every case covers four prefill
and four single-token positions per selected layer. This does not establish
production rare-route coverage or numerical equivalence of any recoding.

All raw hashes pass. Receipt SHA256:
`5bfe6b7014c61786a9afab361fde295a90779f7b34b0caed9d56ec36f5eaf4e8`.
Compact result: `evidence/AW-0036-activation-results.json`.
Pressure remained 1, sampled swap growth 0, and P1 preflight passed after every
owned process ended. Existing build warnings are preserved in the build log;
no claim of a warning-free or full-runtime-test build is made.

Disposition: source activation fixtures admitted for the next diagnostic rung.
Next establish original fast8 GPU projection/mixture references, then screen
candidate representations against these inputs and complete physical accounting.
Candidate-accumulated behavior and full-path capability remain unproven.
