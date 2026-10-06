# AW-0197: Capacity guarded current-history cache replay

Status: F16 terminal and audited; stationary arm live, pair unresolved.

Retry AW-0196 under a new immutable external plan/directory, preserving the
interrupted run. Same reconstructed AW-0195 history, two fresh F16 then
Q8/stationary-Turbo4 servers, AW-0191 runtime/weights/full vision, native
T1/P.95/k20/minP.05/presence0/repeat1/frequency0/seed42/medium,16K context,
8192 output cap,1800-second request timeout. No proposed tools execute.
Fixed order and sampled trajectory changes imply no causal speed claim.
P1 unchanged; no task score or promotion admission from this replay.

Only added policy is explicit disk capacity:16GiB free before either arm,
8GiB minimum during startup/generation, sampled every0.5s. Save samples,
stop both child process groups on a capacity gate, preserve failure receipt,
and mark remaining arms unattempted. Keep host-pressure/swap/protocol gates.
The regenerated NoMachine log remains outside inference and continues to
grow; this guard protects receipt capacity without manipulating it mid-run.
NoMachine reclamation and AW-0196 interruption remain charged evidence.

Run: `python3 scripts/replay_bonsai_capacity_guarded_history.py`.
Audit: `python3 scripts/audit_bonsai_capacity_guarded_history.py`.
Raw: `/Users/chad/Models/agentwing/evidence/AW-0197`.
Plan pins runner, runtime, current history, strict stream auditor and AW-0196
storage failure. Per-arm raw hashes, terminal outputs, capacity/host traces,
commands and full lifetimes remain external. No overwrite or silent retry.

## F16 terminal, pair unresolved

F16 completed in724.036 s: one valid native bash proposal, terminal
tool_calls/one DONE, clean exits. No tool executed or task score inferred.
Strict hash/stream, independent host trace and capacity replay passed:
pressure1/swap growth0 MiB/minimum sampled free268,486,103,040 bytes.
Generated proposal argument hash matches AW-0196's F16 proposal for this
fixed current history. This is scoped reproducibility, not a speed ratio.
Partial receipt: `evidence/AW-0197-capacity-f16-partial.json`; full audit
and raw hashes external under `/Users/chad/Models/agentwing/evidence/AW-0197`.
Stationary arm still live; complete-pair acceptance unresolved.
