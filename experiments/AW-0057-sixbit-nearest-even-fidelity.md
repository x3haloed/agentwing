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
