# AW-0057 — Six-bit nearest-even fidelity falsifier

Test one fixed alternative to AW-0056 before further representation work:
`code6 = clamp(round_ties_even(source_code / 4), 0, 63)`, reconstruct `4*code6`.
Original group64 BF16 metadata stays byte-identical; four cells pack into three
bytes. Expert size remains 2,555,904 bytes, 76.4706% of source. This preserves
source multiples of four exactly, unlike the midpoint form, and removes its
interior half-code mean error under a uniform source-code distribution. Actual
weight error and routed behavior need measurement; upper-end clipping remains.

Before GPU work, exhaustively compare all 256 source values against independent
enumeration of the 64 representable codes with nearest-even tie breaking.
Every packed expert must unpack exactly to the candidate codes, keep metadata
unchanged and differ from each source code by at most three. No calibration,
task-derived training or selection among several rounding variants.

Use all 72 frozen AW-0036 real source-activation fixtures and authenticated
AW-0037 original stages. Primary gate is unchanged: maximum mixture relative
L2 <=5%, maximum expert-down relative L2 <=10%, plus independent scalar double
implementation agreement <=1e-4. Include all layers 0/20/39, three trajectory
categories and 576 selected experts. Independently recompute saved-stage errors.
Failure rejects this exact representation; no further variants inside AW-0057.

As in AW-0056, execute expanded candidate q8 through original fast8 only for
cheap fidelity screening. Hold source, packed and expanded data explicitly;
this measures neither compressed execution nor memory savings. A survivor
requires uncommon routes and candidate-accumulated validation, then direct
packed arithmetic or fully charged expansion, installation and host residency,
physical storage/memory traffic, cache and compute costs before endpoint work.
The same optimistic read-only Amdahl estimate is about 1.094x, insufficient by
itself for the goal. Do not multiply historical component gains as measured.

Same M1/internal SSD, original qpack/layout/kernel, bounded native supervisor,
model lock, preflight, 300-second timeout and pressure/swap gates. Record source,
binary, kernel, fixtures, source/reference receipts, OS/hardware/compiler/thermal
state. No production runtime, P1, prompt, sampling, corpus, scoring or permission
changes; no held-out execution or endpoint claim.

Command: `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/probe_expert_sixbit_rne.py`.

Status: frozen single-form source-activation screen.

## Terminal result — rejected

All 72 fixtures / 576 experts complete in 9.006945209 seconds with pressure 1
and zero swap growth. Exhaustive nearest-even and pack/unpack checks pass.
Scalar implementation discrepancy is at most 6.5431e-6. Independent saved-stage
and recursive-receipt audit passes. P1 post-run preflight passes.

Nevertheless 3 mixtures exceed 5%, reaching 10.1449%, and 5 experts exceed
10%, reaching 29.7439%. Layer maxima are 2.8943%, 10.1449%, and 3.4604%.
All failed mixtures occur at layer 20 across coding/arithmetic/structured;
expert 17 already has 22.6–23.5% up-projection error before SwiGLU. Expert 175
also shows nonlinear amplification. Preserve the full breakdown without
excluding these identities or positions. Rounding changed both error bias and
individual codes, so the improvement over midpoint is not a bias-only causal
measurement. This exact form is rejected before kernel or bank construction.

Raw: `/Users/chad/Models/agentwing/evidence/AW-0057/20260906T145908.631998Z`.
Receipt SHA-256:
`904ac3f6907307f9d771db25d77777f973c710f18207fa62bdcf6bd88f0cfea6`.
Results and localization: `evidence/AW-0057-sixbit-results.json` and
`evidence/AW-0057-failure-breakdown.json`. No endpoint benefit or promotion.
