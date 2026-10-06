# AW-0073 — Larger history/response capacity, cheap memory admission first

Harness and startup admission pass, 2026-10-05; full inference remains unproven.

AW72 debugging exhausts2048 output tokens before edits. Increasing output alone
at8K would be clamped by pinned Pi. Invoke actual exported clamp function on the
saved pre-failure context: current2048 remains2048, requested8192 at8K becomes
3116, proposed16K retains8192. `evidence/AW-0073-capacity-harness-check.json` pins
module, Node and external context bytes. No model started; this proves only
harness allowance. Source syntax and config/command capacities agree.

Next reproduce `PYTHONDONTWRITEBYTECODE=1 python3 scripts/probe_bonsai_capacity.py`
only after AW72 releases ownership. Full pinned PTQ1 language/Q8 vision, Metal,
16K context, FP16 KV, medium recipe, prompt archive0, recurrent checkpoint cap2,
no context shifting. Sample host pressure/swap and RSS during full model startup,
stop at pressure4 or swap growth>1024MiB; preserve negatives. No build/download or
second inference owner concurrently. Expected KV payload1GiB (512MiB above8K),
not observed admission or physical ownership proof. The probe does not decode
or establish retained-history correctness, final inference peak or utility rate.

If admitted, AW74 tests the unchanged exposed development debugging task with
larger capacities. Do not alter current AW72 or retry it. All task/tool/prompt,
reasoning-effort/sampler/verifier/deadline and host gates remain unchanged; only
capacity increases. KV compression remains a user-requested candidate if this
larger full capacity cannot fit safely; do not label stock q4 as TurboQuant.

Full16K startup reaches health, pressure1, swap growth0, peakRSS7,858,544KiB.
KV buffer1024MiB as expected. Raw evidence:
`/Users/chad/Models/agentwing/evidence/AW-0073/20261006T043811.711064Z`.
Receipt independently verified in `evidence/AW-0073-startup-memory-audit.json`.
Only startup is admitted; AW76 tests exposed debugging with safe malformed-call
accounting before full-profile capability/performance revalidation.
