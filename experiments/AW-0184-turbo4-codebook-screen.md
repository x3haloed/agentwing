# AW-0184 — Turbo4 Gaussian codebook fixed-point falsifier

Hypothesis: native16-entry table satisfies scalar Lloyd–Max centroid stationarity
for Gaussian variance1/128, consistent with normalized128-group proxy. Predeclare
residual<=1e-6 allowing six-decimal table rounding; independent scalar quadrature
relative agreement<=1e-5. No model data/inference/task sampling used.

Analytic Gaussian truncated first/second moments: nearest-cell conditionalmean
residualmax.008543856 rejects stationarity. Existing scalarMSE.0001583866224;
673 Lloyd iterations stationaryresidual9.43e-14 produce MSE.00007422662506,
53.1358% scalarGaussian reduction. Both original1,000,001-point8sigma and
independent1,500,001-point9sigma numerical quadrature agree within threshold.
CPU/Metal float tables equal; half decode rounding not stationarity rescue.
Symmetric candidate16-entry table keeps hypothetical4-bit representation cost.
Phase host pressure1/no growth. No runtime edited or model loaded.

Scope: Gaussian scalar proxy, not exact sphere distribution or norm-corrected
vector objective. Existing codec rescales each reconstruction to original norm;
actual transformed V distributions may differ. This theoretical improvement
cannot establish whole-model quality/speed or claim full Google codec fidelity.
Retain mathematical alternative; screen actual captured norm-corrected early /
mid/late V/attention next before GPU/runtime integration. P1/default unchanged.

Source/parent/cache profile/hardware/OS/host and complete tables/moments/hash pins
in plan and receipt; no harness/vision/tool run or sampling applicable.
Command: python3 scripts/screen_bonsai_turbo4_codebook.py; refuses existing rawdir.
External: /Users/chad/Models/agentwing/evidence/AW-0184.
Manifest: evidence/AW-0184-turbo4-codebook-screen.json.
Disposition: native scalar optimality rejected; candidate retained for screening.
