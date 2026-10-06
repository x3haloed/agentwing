# AW-0178 — isolate K and V late-prefix perturbation

## Status

Running; terminal/native numeric/resource audits pending. No promotion.

## Hypothesis and metric

AW148/AW149 changed both K and V cache formats. Separate q8K and Turbo4V
first-row logit displacement on identical late accumulated prefix to choose the
next complete configuration, rather than attributing longer behavior to V alone.
Frozen four-arm order: F16/F16, q8/F16, F16/Turbo4, q8/Turbo4. First-row full-logit
relativeL2<=.10 and top20 overlap>=.50 provisional technical falsifier inherited
from AW148; does not establish agent quality. Own32 trajectories descriptive.
No endpoint acceptance or fixed-order causal speed claim.

## Fixed conditions and provenance

Same AW148 C++ fixture except independent K/V selectors, same selective model /
native AW137 runtime/modelpins/sourceheaders, 16384ctx/128batch/one sequence /
RS0/flashon, native sampler T1/topP.95/k20/minP.05/pres0/repeat1/seed42.
Input exact AW144 7695-chunk prefix, containing original templated Pi context
plus actual partial reasoning. No new template/render/task/scoring change.
Six real early/middle/late projection input/output captures per own generated
token; all32 full248320 logits rows retained outside Git. Independent auditor
verifies raw hashes, allocations, pressure, prompt bytes, shapes/finite values,
first-logit numeric gates and trajectories against freshly replayed F16 control.

16GBM1/internalSSD, fresh process per arm, uncontrolled warm OS cache. OS /
thermal/hardware/runtime/config/inputs/source/compiler pins in frozen plan.
One model owner, pressure<4, swap growth<=1024MiB, per-arm600s watchdog;
failures retained and remaining arms stopped. Diagnostic only: no tools
attempted and no vision encode in this fixture; full vision stack qualification
remains separately required for any resulting complete candidate.

## Commands and evidence

Compile fixture against existing AW137 native libraries using clang++ -O2
-std=c++17; python3 scripts/run_bonsai_cache_factorial_replay.py.
Then python3 scripts/audit_bonsai_cache_factorial_replay.py; partial flag only
for ongoing observation, never complete acceptance. Compiled/source pins in plan.
Raw: /Users/chad/Models/agentwing/evidence/AW-0178.
Manifest: evidence/AW-0178-cache-factorial-plan.json.
P1/default/deployed runtimes unchanged. Disposition unresolved until terminal.
