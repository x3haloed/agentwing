# AW-0149 — identical full accumulated request behavior

Complete; F16 terminal, Turbo deadline failure. Use hash-verified AW-0145 fourth tool-conversation request
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

## Interim FP16 result

Complete SSE/[DONE], one valid bash proposal, clean client/server exits, pressure1
and zero swap growth. Diagnostic wall715.542s;13779 reasoning characters before
a baseline-reproduction/test proposal. Proposed command does not edit; it was not
executed. Independent raw-hash/identical-request/allocator/protocol checks pass.
Receipt evidence/AW-0149-f16-interim.json. This shows substantial generation also
with FP16, not a cache-causal conclusion, task success, or endpoint timing ratio.
Turbo arm remains pending.

## Final negative comparison

F16 complete valid baseline-check proposal after715.542s; Turbo request-timeout
after1804.430s including cleanup, incomplete tool arguments and no terminal/[DONE].
Neither proposed tool executed; no artifact/task score. Both full raw manifests,
identical request bytes, allocator formats, stream IDs and summary independently
replayed. Pressure1/zero swap growth both; baseline1188.12MiB swap.

Receipt evidence/AW-0149-full-request-terminal.json seals raw audit/summary hashes.
Count two emitted proposals: one terminal/schema-valid, one watchdog-interrupted
before argument completion; zero executed, productivity unestablished. Interrupted
arguments are not a completed malformed tool execution. Keep all failures charged.

Reject Turbo completion screen at fixed deadline. Single fixed-order pair cannot
attribute the AW141 failure to cache or establish an endpoint speed ratio. Cold
full-prefix rendering differs from original incremental server KV history. Both
formats show substantial generation before action. No promotion or task rescoring;
next prioritize execution-cost improvements under unchanged native settings.
