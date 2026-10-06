# AW-0199 — Higher precision rotated value-cache screen

## Status and hypothesis

Completed CPU numerical screen. A theory-derived stationary 6-bit Gaussian
codebook with the existing 128-value signed WHT and F16 norm correction
reduces actual V and attention relative L2 by at least 50% in every early,
middle, late fixture compared with stationary 4-bit. Acceptance fixed before
measurement; exact 4-bit packed/decoded fixture parity also required.

## Fixed configuration and commands

Full source, codec, library, parent artifact, fixture, model profile, harness,
hardware, OS, storage and thermal provenance in the receipt. Saved AW109 own
activation captures, layers 3/31/63, 4 KV heads, 48 tokens, 256 dimensions;
24 query heads. No inference, tasks, tools, sampling or reasoning performed.
Model/runtime identity inherited from pinned stationary profile and AW185;
this is not a fresh model or held-out task comparison. Internal SSD, 16 GB M1.
Build command recorded in receipt. Run:

```
python3 scripts/screen_bonsai_value_precision.py
python3 scripts/audit_bonsai_value_precision.py
```

Runner creates immutable external plan before numerical work. Reproduction
requires a fresh external output location; preserve old attempts.

## Results

| Layer | V L2, 4-bit → 6-bit | Attention L2, 4-bit → 6-bit |
| --- | --- | --- |
| 3 | .096730 → .024840 | .051720 → .013080 |
| 31 | .094941 → .024816 | .070238 → .018541 |
| 63 | .094209 → .024438 | .055247 → .013814 |

All declared numerical gates pass. Baseline packed and decoded bytes exactly
match AW185. Independent integer unpacking matches decoded encoder bytes;
scalar math.fsum attention recomputation agrees within 1e-12. Gaussian MSE
independently quadrature checked. Host before/after gate passes; continuous
inference monitoring was not performed or claimed. Single CPU encode timings
are diagnostics only, not performance measurements.

Layout: 100 bytes per128 values (96 payload +4 header), versus68 at4bit and256
F16: 47.1% larger than4bit, 60.9% smaller thanF16. Hypothetical 16K V allocation
200 MiB, Q8K+V472 MiB; allocation arithmetic does not predict RSS or utility.

## Deviations, evidence and disposition

First helper build lacked runtime rpath; loader failed before fixture work.
Preserved its plan and binary under external attempt-0-missing-rpath, then
rebuilt with explicit rpath. No gate or numerical algorithm changed.
Raw evidence: `/Users/chad/Models/agentwing/evidence/AW-0199`, hashes and
summary in `evidence/AW-0199-value-precision-screen.json`.

Retain a numerical survivor for isolated native Metal writer/consumer cost
and correctness checks, then own accumulated trajectories, vision/tool and
endpoint gates if those pass. Shared native inverse WHT is not independently
verified here. This is rotated scalar quantization with norm correction,
not full Google PolarQuant/QJL. No runtime/profile/default or P1 change;
no agent work-rate, universal quality or endpoint qualification claim.
