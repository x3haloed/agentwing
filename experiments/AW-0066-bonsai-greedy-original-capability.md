# AW-0066 — Complete original capability screen for temperature-zero Bonsai

## Status

Running, 2026-10-05. Successor campaign remains active and unqualified.

## Hypothesis / Primary metric

The temperature-zero configuration retained by AW-0065 preserves all eight
unchanged original Stage A v1.1 tasks, with valid protocol and host gates.
Require eight independent successes in manifest order. Stop at first failed
utility, host or protocol result, preserving remaining tasks as unattempted.
One correct data trial is insufficient. No tuning or retry inside this screen.

## Fixed conditions and identities

Exactly AW-0065's model bytes, Prism Metal runtime, Q8 vision, 8192 context,
medium reasoning, 2048-token output, temperature 0, top_p 0.95, top_k 20, min_p
0.05, zero frequency/presence penalties and repetition multiplier 1. Same P1
compact system instruction, bash availability, fixed workspace and permissions.
P1 control remains immutable. Candidate reasoning/output/context/sampling differ
from P1: this is a capability diagnostic, not matched performance or promotion.

Fixed 16 GB M1, internal SSD, macOS 27.0.1 (26A434), one fresh model owner per
task, 900-second Pi and 60-second startup deadlines. No model/build/large
integrity-read work concurrently. Record ambient cache, swap, pressure and
thermal state; stop at critical pressure >=4 or peak swap growth >1024 MiB.
No grader/authority content enters the workspace or prompt. All 215 expanded
corpus inputs are checked, with held-out tasks still unexposed. Pins are frozen
in evidence/AW-0066-original-plan.json before execution.

## Commands / Cheap falsifier

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_greedy_capability.py --freeze
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_greedy_capability.py --check-only
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_greedy_capability.py
```

## Evidence / Accounting

Live run: /Users/chad/Models/agentwing/evidence/AW-0066/20261006T030925.719807Z. Source snapshots are preserved alongside the frozen plan.
Archive task workspaces/state by rename only after owned processes stop. Preserve
commands, events, host samples, independent grades and recursive hashes. As in
AW-0064/0065, receipt generation and initial integrity preflight are outside the
printed diagnostic timer: no final promotion/accounting claim is permitted.

## Conclusion / Disposition

Unresolved. Eight successes permit expanded development, not promotion. The
>=25% two-pair interleaved complete-path gain, solved-task/category preservation,
matched comparison policy, all-overhead timing and broad capability gates remain
mandatory and unproven. No task narrowing, held-out tuning or discarded failure.
