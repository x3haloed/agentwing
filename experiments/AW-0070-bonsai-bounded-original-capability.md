# AW-0070 — Full original capability with bounded saved state

Running 2026-10-05; successor remains unqualified.

Require eight successes on unchanged original tasks in manifest order. Stop at
first failed utility, protocol or host gate, preserving all unattempted tasks.
Use AW69 supported thinking (T1,p.95,k20,min_p.05,presence0,repeat1,freq0), medium
effort, 2048 output, full8K context and vision. Prompt archive cache0; limit
saved recurrent checkpoints to2 instead of32. Eviction trades prefix reuse for
recomputation, not logical history or reasoning. Context shifting disabled.
No retries, task changes, authority exposure or scoring changes. Same prompt,
bash, workspace boundary, 900sec per task and existing pressure/swap gates.
Frozen inputs: `evidence/AW-0070-original-plan.json`.
Command: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_bounded_capability.py`.
Raw run location appears in ignored `var/AW-0070-driver.log`; complete receipts
and source/config pins are retained externally. All215 P2 files match the freeze;
held-out tasks remain unexposed. No matched-P1 or promotion claim from this screen.

## Interim completed-task evidence

First two tasks independently pass grade/protocol replay; full selection remains
running. `evidence/AW-0070-first-two-component-notes.json` records exact saved
log/result hashes and native timing extraction. Navigation118.404s, single-file
fix340.205s. Both pressure1 with zero swap growth. Fix has41.200s prompt work and
294.022s decode for1595 generated tokens across6 requests, plus other task wall.
One BSD sed failure is recovered by a portable file rewrite and tests. This
trace does not establish checkpoint recomputation as the delay cause: decode
dominates. No universal sampler/cache performance conclusion, partial-suite
rate promotion, task shortening or reasoning restriction follows.
