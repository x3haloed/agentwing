# AW-0149 — identical full accumulated request behavior

Running, F16 arm first. Use hash-verified AW-0145 fourth tool-conversation request
and actual renderer, with unchanged native T1/top_p.95/top_k20/min_p.05/presence0/
repeat1/seed42/medium, output8192, context16K, full Q8 vision configured/resident,
no-shift/cacheRAM0/checkpoints2. Same pinned server/artifact/libraries in both arms;
only FP16 K/V versus q8-K/Turbo4-V changes. Tool schema remains identical, but
returned proposals are retained rather than executed: this is one-request behavior,
not agent completion, task score, permission change or endpoint utility comparison.

Fresh one-owner server each arm, startup60s/request1800s and existing host gates.
Fixed F16/Turbo order is an unreplicated diagnostic, not a causal speed comparison.
Capture every raw SSE event and terminal/[DONE] state, server/client logs and host
samples; watchdog failures retained. Large evidence outside Git at
/Users/chad/Models/agentwing/evidence/AW-0149. Plan/source/runtime/request/hardware/
OS/storage/cache/thermal pins: evidence/AW-0149-full-request-plan.json.

Command python3 scripts/replay_bonsai_full_request.py. AW-0141 failed score remains
unchanged. No restricted reasoning, task/deadline/scoring waiver or P1 promotion.
Next independently replay all response events, classify terminal proposal syntax
and investigate long-generation recurrence before further capability work.
