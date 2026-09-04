# AW-0022 — Guard paired metric assessment

## Status

Completed offline infrastructure check; no endpoint or scoring change.

## Hypothesis and falsifier

A reusable pair checker rejects incomplete or unsuitable evidence even when
its aggregate rate exceeds twice the floor. Run it against the real archived
full baseline and AW-0019's single config task: the tempting numeric ratio must
not pass. Also test insufficient successes, a weak absolute historical rate,
critical pressure, excessive swap, and undeclared salvage.

## Implementation

`scripts/assess_stage_a_pair.py` replays both evidence audits and checks full
frozen task order, matching recorded suite/timeouts/tools/storage/OS, positive
elapsed time, successes, recomputed endpoint rates, pressure/swap, recorded
loopback binding, and declaration of candidate salvage. It uses existing acceptance
thresholds without changing verifiers or task scores. Model-error replies,
rejected outputs, and declared salvage remain reported diagnostics.

## Results

Ten Python tests pass, including four pair-check regression tests. The real
baseline/config-task comparison is rejected despite its arithmetic 2.812 ratio:
the candidate is not a full suite and has only one success. Both underlying
run audits pass. See `evidence/pair-gate-partial-run-rejection.json`.

## Limitations

This proves necessary metrics for one pair, not promotion. It does not certify
interleaved scheduling, same-arm identity across two pairs, observed network
binding, permission enforcement, runtime reconstruction, or current protocol
fixtures. Those remain separately evidenced requirements. Ratio output for
unmatched task selections is diagnostic arithmetic, not a valid speed claim.

## Disposition

Retain as offline evaluation infrastructure. The live AW-0019 screen's runner,
model, prompts, tool permissions, and scoring are unchanged.

## Gate correction

The first implementation treated every model error/rejected output/salvage as
an automatic pair failure. That went beyond the frozen accepted-utility rule
and conflated explicit recovery or generation failure with protocol corruption.
The helper now preserves the scorer's verified outcome and reports these counts
separately. Salvage must be declared in the manifest; silent recovery still fails.
Evidence audits and separately required protocol tests/integrity review remain.
This removes an extra gate; no benchmark score or promotion threshold changes.
