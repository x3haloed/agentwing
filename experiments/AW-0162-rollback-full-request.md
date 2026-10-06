# AW-0162 — full native request with bounded history speculation

## Hypothesis and primary metric

Isolated full server with eligible ngram2/3 and three bounded recurrent rollback
slots can complete the unchanged AW149 accumulated request with valid terminal
SSE/tool schema and existing host gates. Primary metric: completion/protocol /
host safety, not speed or task utility. All failures preserved.

## Frozen conditions

AW158 runtime build plus AW157 allocation patch, exact selective Bonsai27B model
and full local vision. Native thinking T1/topP.95/topK20/minP.05/pres0/repeat1,
medium reasoning,8192 output ceiling, context16384,one rollout, q8K/Turbo4V,
no context shift,cacheRAM0, native PTQ multicol enabled. Same whole native OAI
request as AW149; assert structural equality before launch and pin prior plan.
No reasoning/task/tool/permission/verifier narrowing. No tool proposals execute
in this diagnostic. It cannot produce a task utility score.

Full model/runtime/harness/profile/prompt/request hashes, M1/16GB/internalSSD /
OS/thermal/cache, command/environment frozen in external plan before launch.
One model owner; loopback; startup60s/request1800s watchdog and pressure<4 /
swap growth<=1024MiB. Capture every SSE line and attempted tool proposal, valid /
malformed/incomplete distinguished. Worker source pinned. Final protocol audit
verifies raw/request/allocator/host/terminal completion and proposed tool schema.
Single new candidate run; historical AW149 is NOT a replicated interleaved
control and supports no speed ratio or causal attribution.

## Commands and evidence

python3 scripts/replay_bonsai_rollback_full_request.py
python3 scripts/audit_bonsai_rollback_full_request.py --partial while terminal
rows accumulate; final auditor after completion.
External frozen plan/SSE/native log/pressure and final raw-hash results:
/Users/chad/Models/agentwing/evidence/AW-0162.

## Disposition

Planned completion screen, not promoted. AW160 timeout remains negative; early
numeric cases AW160/AW161 are technical evidence only. P1/defaults unchanged.
Live progress and final disposition must follow authoritative process/results.

## Initial live evidence

Request equality/profile/harness pins verified. Server/worker/parent confirmed
live; native log records real target verification batches including partial /
zero acceptance without logged checkpoint restoration so far. Reasoning SSE is
streaming, pressure1. Nonterminal snapshot outside Git; it is not completion or
sampling fidelity evidence. Managed exec session56967 must be revalidated on
continuation, and the same handle watched until terminal rather than restarted.
