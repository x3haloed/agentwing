# AW-0197: Capacity guarded current-history cache replay

Status: terminal; F16 valid, stationary timeout, screen failed. Retained negative evidence.

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

## Complete failed screen

F16 completed with one valid proposal in724.036 s/13,503 thinking characters.
Q8 K/stationary Turbo4 V timed out in1804.545 s with29,902 thinking
characters,7769 SSE events, no terminal marker and no executable proposal.
Neither arm executed tools or scored a task. Same request bytes/sampling,
runtime and model weights; both K and V representations change together,
so this does not isolate V alone or establish a general causal speed ratio.

Independent raw hash/strict stream/host/capacity audits preserve the failed
screen. Pressure peak1/swap growth0 in both arms. Stationary minimum free
226,900,209,664 bytes excludes disk exhaustion as this run's stopping cause.
No live model owner remained after cleanup. Terminal receipt
`evidence/AW-0197-capacity-current-history-terminal.json` pins external full
audit/raw hashes under `/Users/chad/Models/agentwing/evidence/AW-0197`.
AW-0196 storage interruption remains preserved and is not silently waived.

Reject this cache configuration for promotion; retain valid F16 response
and negative stationary trajectory. Next split K/V precision on this same
history before modifying quantization or another expensive endpoint run.
No task, reasoning, output-budget, deadline or scoring relaxation. P1 frozen.
