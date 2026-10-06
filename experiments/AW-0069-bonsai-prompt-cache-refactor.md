# AW-0069 — Supported-thinking refactor with prompt archive cache disabled

Completed and retained, 2026-10-05. Diagnostic only, not a successor promotion.

Cheap falsifier following AW66 host rejection and AW68 allocation evidence.
Use the unchanged original refactor task/verifier, full 8K context, medium
reasoning, 2048 output budget, Q8 vision and PTQ1 language weights. Explicit
thinking sampling T1, p.95, k20, min_p.05, presence0, repetition1, frequency0.
Disable optional server RAM prompt-state archive (`--cache-ram 0`); keep active
KV reuse. Disable context shifting and log allocations at verbosity5. Same
900-second deadline, fixed workspace, bash and permission boundary. Pressure4
or swap growth over1024MiB aborts. No held-out task exposed.

Not an isolated AW66 cache ablation: sampler also returns from unsupported
T0 to publisher T1. Not a performance comparison. Failure remains evidence.
Frozen plan `evidence/AW-0069-refactor-plan.json` hashes all relevant inputs.
Raw evidence `/Users/chad/Models/agentwing/evidence/AW-0069/20261006T033203.697908Z`.

Reproduce: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_cache_refactor.py`.
Check immutable inputs with `--check-only`; never overwrite the frozen plan.
Independent terminal audit `evidence/AW-0069-terminal-audit.json` passes raw
hashes, grade replay, native tool/request pairing and unchanged original tests.
Task utility1, wall205.728s; diagnostic total209.663s excludes receipt creation.
Pressure1 throughout, swap growth0. Four valid productive tool calls: bounded
exploration, source/test read, shared implementation write, symbol/test check.
Failed, malformed, denied and redundant calls0. Recurrent checkpoints peak at
three observed 149.626MiB states, separate from active recurrent state and KV.
Optional prompt archive is confirmed disabled, supported sampling values are
confirmed in native request logs. Full 8K history remains; no performance gain
or attribution of AW66's failure is established by this unpaired realization.
AW70 advances to all eight original tasks with two saved recurrent checkpoints,
not a shorter context. Held-out panel remains unexposed.
