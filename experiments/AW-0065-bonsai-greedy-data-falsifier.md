# AW-0065 — Temperature-only falsifier for the Bonsai data failure

## Status

Completed, 2026-10-05. AW-0064's negative original-capability result is preserved.

## Hypothesis and primary metric

Bonsai under deterministic temperature zero can satisfy the unchanged original
05-data-transform task, rather than AW-0064's incorrect successful-event count.
Primary metric: independent original utility 1 with valid protocol and host gates.
One attempt only, no tuning or retry in this experiment. A pass does not establish
causal sampler improvement, eight-task preservation or broader capability.

## Fixed conditions / Pins

Same admitted model, runtime, full local vision stack, medium reasoning,
2048-token ceiling, 8192 actual context, top_p 0.95, top_k 20, min_p 0.05, zero
presence/frequency penalty and repeat penalty 1.0 as AW-0064. Only temperature
changes from 1 to 0, explicitly in the server and Pi model samplingParams.
Original task, grader, P1 compact instruction, bash availability and permissions
remain unchanged. Same fixed workspace path and archive-by-rename policy,
900-second Pi deadline, 60-second startup cap; one model owner on internal SSD,
16 GB M1, macOS 27.0.1 (26A434). Pressure <4 and peak swap growth <=1024 MiB.
Do not feed the model the observed wrong count, expected count, or this record.
No held-out task is exposed. Configuration and source hashes frozen in
`evidence/AW-0065-data-plan.json`.

## Cheap falsifier / Commands

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_greedy_data.py --freeze
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_greedy_data.py --check-only
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_greedy_data.py
```

## Evidence and accounting

Raw evidence external under /Users/chad/Models/agentwing/evidence/AW-0065.
Record all tool events, host samples, startup/tool/grade wall and recursive hashes.
As in AW-0064, final receipt creation and initial source/profile preflight are
outside the reported diagnostic timer. This cannot support final promotion
accounting; task success, not the diagnostic rate, is the primary metric.

## Conclusion / Disposition

Retained for a new complete frozen original screen, AW-0066; not promoted.
Run /Users/chad/Models/agentwing/evidence/AW-0065/20261006T030339.427325Z passed the unchanged grader and independent hash/protocol/regrade audit. Correct successful_events=4; full task wall 130.311 s and diagnostic wall 134.230 s. Pressure peak 1, zero swap growth. Three valid calls: two productive (source inspection and artifact write), one redundant assertion of the same constants; no malformed, denied or failed calls. Assertions were circular verification, not independent CSV computation. Evidence: evidence/AW-0065-terminal-audit.json. A source snapshot is preserved in the sibling external directory ending -source-snapshot, without altering the original raw receipt.

This differs from AW-0064's one failed trial but is not an interleaved causal
sampler result. A positive single-task result only allows a new complete frozen
original capability screen before expanded development. A failure rejects this
exact diagnostic configuration. P1 and the original/expanded task sets remain
frozen; all >=25% replicated full-path and category preservation gates remain.
