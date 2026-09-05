# AW-0028 — Usable local agent handoff

Disposition: in progress; AW-0027 paired validation has passed. This experiment
adds a task launch path without modifying the frozen benchmark execution files.

Hypothesis: the exact validated prompt, Pi profile, runtime and permissions can
be exposed for a user-supplied workspace/task while retaining bounded process
lifetime, loopback service and host stop conditions.

Inputs: `spec/validated-local-agent.json`, `config/pi-models-validated.json`,
`config/validated-local-agent-prompt.txt`. The last two are byte-identical to
A2's archived files, verified in `evidence/AW-0027-handoff-input-check.json`.
AW-0026 clean-build and AW-0024 protocol raw hashes also rechecked successfully.
The original frozen-plan preflight still passes after all four measurements.

Required validation before handoff: help/preflight without launching a model;
synthetic lifecycle tests for success, client failure, timeout, memory-stop and
owned descendant cleanup; real Pi boundary fixture through the task path; a
short separately labeled real-model smoke. Preserve task artifacts and raw
logs outside Git. A new task's Pi exit is not verifier-weighted benchmark
utility; do not combine handoff smokes with the four frozen runs.

The launcher should accept a workspace and task file, preserve the input
workspace by using a run-local copy, create fresh boundary state and archive
output. It must pin the original runtime executable, exact prompt/models,
limit to one model owner, stop on pressure>=4 or swap growth>1024MiB, use a
900-second task deadline, stop owned process groups on all exits, and leave
127.0.0.1:8080 free. No new context or recovery optimization belongs here.

Implementation checkpoint: `scripts/run_local_agent.py` now provides hash/host/
ownership preflight and private workspace copies with task logs, a 900-second
client deadline, host stop conditions and process-group cleanup. Five lifecycle
tests pass, including descendant cleanup after parent exit and timeout evidence.
The first real Pi fixture at `protocol-20260905T070049Z` exposed a Darwin signal
error on an exited, unreaped server group; no process/listener remained. It is
preserved as a failed handoff trial. Reaping and checking group membership before
signaling fixes that path. The repeated real Pi fixture at
`protocol-20260905T070141.590602Z` passes all five tool results, expected failed
command/recovery and output verification, under the unchanged task boundary.
See `evidence/AW-0028-launcher-protocol.json`. Real-model smoke remains pending.
