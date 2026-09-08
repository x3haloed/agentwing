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

## C1 terminal — shared failure reproduced

C1 finishes with utility 0 in 272.784372209 seconds, valid protocol, maximum
pressure 2 and zero swap growth. Frozen grader replay and configuration/receipt
checks pass. All nine structured visible events match AW-0058 exactly after
removing generated call IDs, including the wrong answer 1000. This is evidence
against attributing that visible failure specifically to the candidate runtime;
it is not hidden-state equivalence or a path-only causal attribution. Continue
A1 then C2 unchanged. No utility-rate gain exists from this zero-utility arm.

C1 raw: `/Users/chad/Models/agentwing/evidence/AW-0059/20260908T045929.095918Z`.
Receipt: `4deb69b15b1f46c85c6221c643241aba670858e6253b2019b0237db203251502`.
Audits: `evidence/AW-0059-C1-audit.json` and
`evidence/AW-0059-C1-versus-AW0058.json`.

## A1 terminal — identical visible failure

A1 finishes with utility 0 in 233.703038125 seconds, valid protocol and passing
host gates. Independent record/grader audit passes. Its complete nine-event
visible transcript equals C1 after removing generated call IDs only. Shorter
failed execution is not a utility/hour gain. Continue the frozen C2 control.

Raw: `/Users/chad/Models/agentwing/evidence/AW-0059/20260908T050442.310841Z`.
Receipt: `df163e0bbc04174cde31a4ff37f5a8e4347affbee2655cee188ad32077bf7514`.
Audits: `evidence/AW-0059-A1-audit.json` and
`evidence/AW-0059-C1-A1-visible.json`.

## Terminal comparison — shared failure confirmed, no utility gain

C2 finishes with utility 0 in 262.123784458 seconds. All three arms pass
configuration/receipt, protocol, host and independent frozen-grader replay.
All nine structured visible events are identical across C1/A1/C2 after removing
generated call IDs only. Every arm writes development default 1000, overlooking
the production.env override of 2750. The recorded pressure intervals establish
C1/A1/C2 order without overlap; the sum of charged arm walls is 768.611194792 s.

Retain this as a completed attribution diagnostic: the exact candidate did not
introduce a distinct visible failure on this matched slice. This does not prove
hidden-state equivalence, explain historical workspace/setup sensitivity, or
restore original-suite preservation. All utilities are zero; shorter candidate
wall is not a utility-rate improvement. No promotion or further AW-0059 attempts.

C2 raw: `/Users/chad/Models/agentwing/evidence/AW-0059/20260908T050901.081651Z`.
Receipt: `4728745e52d7810c1ef053af5451628555c89be170a95877e42450ed78017782`.
Full comparison: `evidence/AW-0059-comparison-audit.json`, containing each arm's
receipt, grading audit and pairwise visible comparison. P1 preflight passes;
all experiment processes are terminal. P1 and the held-out panel are unchanged.
