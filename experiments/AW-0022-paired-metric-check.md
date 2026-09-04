# AW-0022 — Guard paired metric assessment

## Status

Completed offline infrastructure check; no endpoint or scoring change.

## Hypothesis and falsifier

A reusable pair checker rejects incomplete or unsuitable evidence even when
its aggregate rate exceeds twice the floor. Run it against the real archived
full baseline and AW-0019's single config task: the tempting numeric ratio must
not pass. Also test insufficient successes, a weak absolute historical rate,
critical pressure, excessive swap, and model-error replies.

## Implementation

`scripts/assess_stage_a_pair.py` replays both evidence audits and checks full
frozen task order, matching recorded suite/timeouts/tools/storage/OS, positive
elapsed time, successes, recomputed endpoint rates, pressure/swap, recorded
loopback binding, and candidate protocol counters. It uses existing acceptance
thresholds without changing verifiers or task scores. All candidate calls must
have zero model-error replies, rejected outputs, and salvaged prefixes.

## Results

Nine Python tests pass, including three pair-check regression tests. The real
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
