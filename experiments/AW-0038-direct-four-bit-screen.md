# AW-0038 — Direct four-bit expert execution, first fidelity screen

Predeclared candidate: reuse each source 64-weight affine group, map unsigned
q8 to nearest q4 by floor((q8+8)/17), multiply its BF16 scale by 17 and round
back to BF16 (ties-to-even), retain its original BF16 bias. Pack two codes per
byte and execute P1's existing fast4 kernel, SwiGLU and routed accumulator.
Artifact size is 1,769,472 bytes/expert (52.94% of P1), including metadata.
This is a modified representation, not lossless compression.

Measure all 72 source-activation fixtures against AW-0037 stage references.
Primary continuation screen: maximum routed-mixture relative L2 <=5% and maximum
expert-down relative L2 <=10%. These are provisional cheap rejection thresholds,
not agent-capability guarantees or imported Firewing acceptance criteria. Passing
only permits deeper accumulated-trajectory and physical-path investigation.
Original task-success preservation remains the promotion authority.

Independently verify candidate affine projections and SwiGLU at <=1e-4 relative
L2 against scalar double arithmetic of the candidate bytes. Preserve all stage
outputs and numerical failures; no full expert bank conversion, model load,
held-out execution, production patch or speed claim. Same bounded supervision and
host gates as AW-0037. Read 8-bit source bytes for this on-the-fly diagnostic;
it is not a measurement of compressed storage or inference throughput.

## Result — rejected

All 72 fixtures and 576 expert executions completed. Candidate arithmetic agrees
with its independent double reference: maximum projection relative L2 4.293e-6,
below the 1e-4 implementation gate. Source/reference identities and stage hashes
were checked. Against original fast8 outputs, however, 71/72 routed mixtures
exceed 5% relative L2 and 473/576 expert-down outputs exceed 10%. The maxima are
38.672% and 137.616%, respectively. Mixture medians at layers 0/20/39 are
8.219%, 13.066%, and 8.113%.

Reject this group64 scale-times-17 form at the predeclared continuation screen.
No bank conversion or agent run is justified by this result. It does not reject
all four-bit methods, establish accumulated-model behavior, or measure an agent
capability regression. The implementation check separates representation error
from an incorrect kernel/data-layout implementation.

Raw evidence: `/Users/chad/Models/agentwing/evidence/AW-0038/20260906T063710.128423Z`.
Receipt SHA256: `8a0f48fa25af1ae395209763f19a897edcc6a4fbadbdcdbd5bfbbf17ae7ff85b`.
Summary: `evidence/AW-0038-fourbit-results.json`. The run exited 0 in 5.778 seconds,
including source reads, recoding and CPU checks; this is not throughput evidence.
Pressure remained 1 and swap growth 0 MiB. Post-run P1 preflight passed.
The diagnostic retains a source-sized allocation while recoding in place, so
52.94% is candidate artifact size, not a measured residency reduction.
