# AW-0193: Stationary cache full accumulated request replay

Status: complete; both arms passed terminal stream/hash/host audit. Retained experimental; no endpoint promotion.

Replay the exact AW-0145 saved native Pi fourth request, with the existing
AW-0149 explicit 8192-token cap, native thinking sampling and medium effort.
Use the pinned AW-0191 server and full vision projector. Two fresh-server
arms use stationary Turbo4 V/Q8 K first, then F16 K/V. This is a fixed-order
behavior diagnostic, not a speed comparison or autonomous task score.
No proposed tools execute. P1 remains unchanged.

The runner enforces successful `evidence/AW-0192-stationary-admission.json`
before launch, freezes its full plan under the external evidence directory,
and preserves failures, request bytes, raw streams, logs and host samples.
The auditor reuses AW-0163 strict stream parsing, including duplicate DONE,
data after DONE, changed IDs, duplicate JSON keys and non-finite arguments.

Raw evidence destination: `/Users/chad/Models/agentwing/evidence/AW-0193`.
Run: `python3 scripts/replay_bonsai_stationary_full_request.py`.
Audit: `python3 scripts/audit_bonsai_stationary_full_request.py`.
Complete valid tool proposals are a prerequisite for another expensive
expanded multi-file task; this diagnostic alone cannot promote a successor.

## Candidate terminal, pair still running

The stationary Turbo4/Q8 arm completed in 1707.336 seconds with one
schema-valid bash proposal and clean terminal `tool_calls`/one DONE. No
tool executed and no task score is inferred. Strict stream/hash audit and
independent host-trace replay passed: peak pressure 2, swap growth 0 MiB.
The 26,341 thinking characters and all startup/decode overhead remain
charged. Partial receipt: `evidence/AW-0193-stationary-candidate-partial.json`.
Full audit including generated arguments remains external at
`/Users/chad/Models/agentwing/evidence/AW-0193/partial-candidate-audit.json`.
F16 is still running; AW-0194's complete-pair gate remains closed.
This reverses the old cache's incomplete-response result for this one
request only; it does not prove task utility or a causal performance gain.

## Complete pair

F16 completed in 745.972 seconds with 13,779 thinking characters and one
valid bash proposal; stationary Turbo4 completed in 1707.336 seconds with
26,341 thinking characters and one valid bash proposal. Neither executed
a tool. Both had one terminal tool_calls/DONE, clean client/server exits,
independently replayed host traces and zero swap growth; pressure peaks
were 2 (stationary) and 1 (F16). Different generated proposals and fixed
arm order preclude causal speed attribution. No task success is claimed.

Receipt: `evidence/AW-0193-stationary-full-request-terminal.json`; external
full audit and raw hashes: `/Users/chad/Models/agentwing/evidence/AW-0193`.
The AW-0194 complete-pair gate is satisfied, and its frozen-input/corpus
integrity check passed. Prior partial receipt remains preserved.
