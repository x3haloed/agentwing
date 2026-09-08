# AW-0059 — Matched original-navigation comparison

Hypothesis: the AW-0058 wrong-answer trajectory is shared by frozen P1 under
identical conversation/setup conditions, rather than introduced by the exact
candidate. Run C1 (P1), A1 (AW-0047), C2 (P1), in that frozen order, each on
original 01-navigation with fresh server/Pi and the same fixed workspace path.
Compare independently graded utility and complete visible event sequences,
normalizing generated call IDs only. Divergence remains evidence requiring
localization; matching visible outputs do not prove equality of hidden state.

All task files, prompt, sampler, 512-token ceiling, model bytes, 0.5-GiB cache,
permissions, verifier and protocol rules remain pinned and unchanged. The sole
arm differences are the pinned runtime binary/kernel and its five exact-feature
flags. Copy-grade artifacts with the existing unchanged original verifier.
900-second task deadline, 60-second startup gate, pressure <4 and swap growth
<=1 GiB. Own and clean server/client process groups; preserve all attempts.

Semantic utility 0 does not stop this causal diagnostic: both controls are
needed to interpret it. Stop the sequence on host, execution or protocol failure.
Each next arm may launch only after the previous terminal record is audited.
No automatic rerun or feedback tuning. Initial AW-0058 failure remains intact.

Count staging, startup, task/tool and grading wall. Static admission checks
precede the arm clock and are separate, so this is not final promotion accounting.
Zero-utility elapsed-time savings establish no utility/hour gain. Historical P1
suite runs have different staging/lifecycle and are not matched comparisons.
Even three successful arms cannot establish broad capability or the goal.

Frozen inputs: `evidence/AW-0059-screen-plan.json` plus P1 preflight and the
candidate's pinned profile. No held-out model execution or production edits.

Commands, in order:

```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_matched_navigation.py --task 01-navigation --slot C1
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_matched_navigation.py --task 01-navigation --slot A1 --candidate-plan spec/joint-development-candidate.json
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_matched_navigation.py --task 01-navigation --slot C2
```

Status: frozen; C1 pending launch.
