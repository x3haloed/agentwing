# AW-0177 — native row8 source and selected-pipeline audit

Hypothesis: AW176 selected the changed single-column decoder, not a fallback.
Read-only source and completed raw-log inspection, no inference/performance run.
Symmetric3531-file inventory and byte hashes identify exactly one changed file:
ggml-metal-impl.h N_R0_PTQ1_0 from4to8. Host dispatcher uses that macro for row
layout and selected shader instantiates kernel_mul_mv_ptq1_0_f32_impl with it.
Both candidate logs select single-column nsg1/ne12=1/r2=1/r3=1 kernel, with
thread execution width32 and compiled max-threadgroup limit576 versus832 in
both native controls. Independent source and log hashes in receipt.

Retain source/pipeline authority evidence. This supports AW176 measuring its
intended changed implementation. The compiler limit difference does not measure
register occupancy/spilling or establish why timing gain was negligible.
AW176 cost rejection stands. No endpoint result, performance promotion, model /
P1/profile/task/permissions/sampling change. Runtime/config/hardware/provenance
inherit hashed AW176 receipt; no new timing claim.

External: /Users/chad/Models/agentwing/evidence/AW-0177/audit.json.
Manifest: evidence/AW-0177-native-row8-authority.json.
