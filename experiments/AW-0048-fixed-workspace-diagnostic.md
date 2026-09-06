# AW-0048 — Fixed workspace path in the recovery comparison

## Status

Complete, positive development diagnostic. All three arms score 1 and pass
protocol/host gates; candidate utility-rate ratio to pooled controls is 1.80695.
The primary control-repeatability prediction is supported. AW-0047 remains
terminal and negative. No promotion.

## Hypothesis

Holding the model-visible workspace and private-state paths constant removes
the concrete path-text confounder found immediately before the first divergent
recovery repairs in AW-0047. The testable behavioral prediction is that the two
P1 controls produce the same visible transcript through their first repair when
their preceding visible inputs agree. Failure of that prediction rejects path
variation as a sufficient explanation. Agreement cannot establish exact wire
token identity or prove that path variation caused the earlier failures.

## Configuration identities and fixed conditions

P1 remains the immutable control from `spec/validated-local-agent.json`.
The unchanged candidate is `spec/joint-development-candidate.json`: AW-0047
runtime 4dff62e867d62288d4224974c4add523dad50437, with full expert overlap,
bounded oversized-union streaming, and strict accepted-tool history retention.
Its earlier failed capability-preservation result remains recorded.

Only the development harness workspace placement changes in both arms. The
generic live path `/Users/chad/Models/agentwing/active/workspace` is selected
before outcomes and will not be tuned. The existing boundary gives each attempt
fresh adjacent `/Users/chad/Models/agentwing/active/agentwing-task-state`.
After owned client/server processes stop, both directories are renamed into
that attempt's unique evidence directory. No task input, prompt, model, runtime,
tool schema, permission policy, validator, grader, generation setting, cache
budget, or timeout changes. The same 16 GB M1/internal SSD is used. Manifest
records OS, thermal state, available storage and all source/binary hashes.
The 215-file AW-0034 corpus freeze and P1 checks must pass before every arm.

## Primary metric and acceptance rule

Primary diagnostic: whether the two controls' first repair commands agree after
an identical structured visible prefix. Compare commands, visible assistant
contents without generated call IDs, and exact tool results; retain raw traces.
Report accepted utility and full measured wall time for C1/A1/C2 as secondary
development evidence. A candidate losing a control success fails preservation;
elapsed time without utility never establishes a gain. Compare pooled control
utility/hour only if its denominator is positive. This single-task diagnostic
cannot qualify the project goal or reverse AW-0047.

Frozen order: dev-recovery P1 C1, unchanged joint A1, P1 C2. Stop remaining arms
on host-gate or protocol failure; ordinary grader failure is retained and the
order continues. Task timeout 1800 seconds; server startup capped at 60 seconds.
No held-out model execution. No selecting a more favorable path or repeating
arms to replace failures.

## Cheap falsifier and commands

Before the model comparison, five lifecycle/boundary tests passed: repeated
fresh inputs at the same path, independent workspace/state archives, exception
preservation, refusal of unowned/unfinished contents or archive collisions,
and actual unchanged sandbox execution allowing scoped writes while denying
a test-owned outside write. These are engineering checks, not speed results.
Candidate check-only admission also passed. Neither loads model weights.

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/test_stable_workspace.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_stable_development.py --task dev-recovery --check-only
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_stable_development.py --task dev-recovery
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_stable_development.py --task dev-recovery --candidate-plan spec/joint-development-candidate.json
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/run_stable_development.py --task dev-recovery
```

Each model arm is launched separately after checking the preceding result and
stop gates. `audit_stable_development.py` verifies all three archived receipts,
grader replay, profile/source pins, actual Pi session cwd, common path policy,
and ordered nonoverlapping execution. Inspect visible prefixes separately.

## Confounders and accounting

Static admission precedes the measured diagnostic clock. All subsequent setup,
model/tool execution, workspace archival and grading enter that clock, but this
is not the final promotion accounting runner. OS cache/thermal variation and
unrecorded raw wire spellings remain possible confounders. Fixed paths control
one observed difference; they do not guarantee deterministic model behavior.
The test is selected using development evidence, so it provides no held-out
generalization estimate. Prior demonstrated successes remain regression gates.

## Evidence and disposition

Frozen pins: `evidence/AW-0048-fixed-workspace-plan.json`.
Large raw evidence: `/Users/chad/Models/agentwing/evidence/AW-0048/`.
Engineering log: `workspace-tests.log`, with its hash in the frozen plan.
Retain the unchanged candidate and fixed-path harness for broader development
screening. No candidate promotion.

### C1 launch

Plan and implementation committed at `f192b83` before model execution.
C1 raw directory is
`/Users/chad/Models/agentwing/evidence/AW-0048/20260906T104140.560820Z`.
The live Pi session confirms cwd equals the frozen workspace path. Initial
pressure is 1, swap 705.31 MiB. These are startup observations, not final gates
or task results. A1 and C2 remain unattempted; inspect C1's terminal summary,
protocol and host gates before advancing. The runner owns process shutdown,
sampling, deadlines and archival even if the surrounding tool call yields.

### C1 completed

C1 earns accepted utility 1 in 1163.357361 measured seconds (3.094492/hour).
All protocol checks pass: 12 tool calls, one reported tool error, two repeated
commands, and 13 requests. Pressure peaks at 1, with zero swap growth.
Independent recursive-receipt and grader replay pass. The workspace and private
state were archived, and the fixed staging root contains only its ownership
marker. Runner/helper hashes and actual Pi cwd match the frozen plan.

The first repair is still call eight, following a different inspection order
than AW-0047. It uses string casefold without Unicode decomposition and passes
both the maintained validator and independent grader. Documentation is saved.
A later full refill processes 1561 tokens despite a 1466-token matching prefix,
costing 405.6 seconds TTFT. This is charged diagnostic model work, not a candidate
gain. A1/C2 remain required and AW-0047's failed preservation remains unchanged.
Small records: `evidence/AW-0048-recovery-C1-audit.json` and
`evidence/AW-0048-recovery-C1-result.json`.

### A1 launch

After C1's terminal audit and successful candidate preflight, A1 started at
`/Users/chad/Models/agentwing/evidence/AW-0048/20260906T110307.710521Z`,
with harness revision `1792ca3`. The live Pi session confirms the same frozen
cwd as C1. Initial pressure is 1 and swap remains 705.31 MiB. These are startup
observations only. C2 remains unattempted, pending A1's terminal host/protocol
checks. Candidate grade and utility rate are not yet known.

### A1 completed

A1 earns accepted utility 1 in 645.059094 measured seconds (5.580884/hour).
Protocol passes with 12 tool calls, one reported tool error, one repeated command
and 13 requests. Pressure peaks at 1 with zero swap growth. Independent receipt
and grader replay pass; profile/source/path pins and archival checks pass.

The first 18 structured visible events match C1 after removing generated call
IDs, including the identical first repair and following validation. The next
assistant narration differs, while the stale-launcher command remains equal.
On that request A1 processes 21 new tokens with 1540 reused, TTFT 5.4 seconds;
C1 processes all 1561 with no reuse, TTFT 405.6 seconds. Total new prompt tokens
are 1113 versus C1's 2605, and generated tokens 982 versus 1057. Visible equality
does not establish unrecorded wire-token equality, and later behavior differs.

The preliminary utility-rate ratio to C1 alone is about 1.80349. C2 and the
predeclared control-repeatability diagnostic remain pending; this is not a
pooled comparison, broad capability result, or promotion. It does not revise
AW-0047's failed preservation result. Records are
`evidence/AW-0048-recovery-A1-audit.json`, `...-A1-result.json` and
`evidence/AW-0048-recovery-C1-A1-prefix.json`.

### C2 launch

After A1's terminal audit and successful P1 preflight, C2 started at
`/Users/chad/Models/agentwing/evidence/AW-0048/20260906T111516.491668Z`,
with harness revision `f267f4b`. It uses the unchanged P1 binary and frozen
workspace policy. The primary C1/C2 repeatability diagnostic and pooled utility
comparison await C2's terminal receipt and grader/protocol audit.

### Completed comparison

C2 scores 1 in 1167.820926 seconds (3.082664/hour), with 12 tool calls, one
reported tool error, two repeated commands and 13 requests. Protocol passes,
pressure peaks at 1, and swap growth is zero. C2 repeats the 1561-token full
refill with 1466 matched tokens, TTFT 408.3 seconds. Receipt/grader replay and
three-arm configuration, order and workspace audits pass.

| Arm | Accepted utility | Measured seconds | Utility/hour |
| --- | ---: | ---: | ---: |
| P1 C1 | 1 | 1163.357361 | 3.094492 |
| Joint A1 | 1 | 645.059094 | 5.580884 |
| P1 C2 | 1 | 1167.820926 | 3.082664 |

Pooled control utility/hour is 3.088567. Candidate ratio is 1.806949, with
control-success preservation and protocol checks passing. The two controls'
complete 25-event structured visible transcripts agree after removing generated
call IDs, including the first repair. This supports the predeclared diagnostic
and using fixed paths for subsequent comparisons; it does not prove path-only
causality for AW-0047 or unrecorded wire-token equality.

The candidate matches both controls through 18 visible events, then differs
in narration and later documentation/validation details while retaining a
successful final artifact. This single development task does not prove broad
capability, satisfy replicated full-path accounting or revise prior failures.
All raw traces, receipts, source pins and outcomes are retained. Final records:
`evidence/AW-0048-recovery-C2-result.json`,
`evidence/AW-0048-recovery-comparison-audit.json`,
`evidence/AW-0048-recovery-visible-comparison.json`, and
`evidence/AW-0048-terminal-ledger.json`.
