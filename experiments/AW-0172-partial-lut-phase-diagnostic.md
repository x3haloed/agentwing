# AW-0172 — partial LUT GPU phase diagnosis

Hypothesis: separately measured GPU/host construction and application windows
identify the dominant cost of the rejected partial-table prototype. No speed
comparison or endpoint metric. Freeze shader/Swift/parent matrix/source/input /
binary/model/runtime/host/OS/thermal/cache identities before work. Original
precision/data/numeric gate unchanged; no task/model/runtime/default changes.

Diagnostic separates producer and consumer into two command buffers and waits
between them. Therefore not a decomposition of AW171's one-buffer timing and
not a matched configuration comparison. Command GPUstart/end intervals and
host build/application/readback windows captured; first warmup retained.
One owner,60s watchdog, pressure/swap gates. All5120finite outputs pass relativeL2
1.63418e-6 versus actual native reference; pressure1/no swap growth1191.12MiB.

GPU build29–52microseconds, application4.26–7.59milliseconds across five retained
iterations. Application dominates this diagnostic. Producer optimization alone
cannot be presumed to resolve cost. Consumer scheduling/gathering/register/
representation causes remain unproven; investigate those instead. Original
AW171 complete-path rejection preserved. Independent raw/output/timestamp-row
replay passes. No integrated model/endpoint performance claim or promotion.

Source experiments/fixtures/bonsai-partial-lut-phases.swift, exact command and
full matrices/native log/binary/output/metadata external
/Users/chad/Models/agentwing/evidence/AW-0172. Manifest
 evidence/AW-0172-partial-lut-phase-diagnostic.json. P1/runtime/default untouched.
