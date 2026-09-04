# AW-0024 — Task write/network boundary integration

## Status

Prepared wrapper only; not in the live runner. Real Pi validation pending.

## Hypothesis

A scoped native write/outbound-network boundary can run the existing Pi shell
protocol without changing task utility, while enforcing denied writes and
connections in descendant tool processes.

## Candidate

`scripts/run_task_boundary.py` prepares fresh private state beside a task
workspace and execs the requested command through `config/task-boundary.sb`.
The policy allows file writes under the canonical workspace, private state,
and `/dev/null`, and outbound network connections only to localhost at the
specified port. The wrapper gives Pi its own state/model configuration and
uses private temporary/cache directories. It keeps the actual workspace cwd.
The existing process-group helper must remain outside it so cancellation still
covers all descendants. Existing state is rejected instead of reused.

This builds on AW-0018's scoped canaries. File reads and other capabilities
remain allowed by default. It is a write/outbound-network policy, not a complete
untrusted-code sandbox or a claim of comprehensive adversarial isolation.

## Cheap falsifier

After the live model suite terminates, use fresh disposable directories to
check workspace/state writes, `/dev/null`, denied outside writes including a
symlink escape, inherited restrictions in child shells, permitted local
connection, and denied other-port connection. Then run real Pi against the
owned protocol fixture using this wrapper and copied model configuration.
Prove all expected tool calls/results and recovery, no unexpected writes,
and child-process cleanup. Retain all failed probes.

## Measurement and acceptance

Before endpoint use, explicitly freeze the policy, wrapper, state policy,
configuration hashes, and command in the runner manifest. Apply the same
permissions in both paired arms. Re-run protocol fixtures and a bounded real
model task before full paired measurement. Preserve the historical score and
label policy changes. Do not silently apply this wrapper to AW-0019's live
screen. Success is verified utility/hour under enforceable recorded boundaries;
passing local canaries alone does not promote a configuration.

## Results and disposition

Source parses. No claim of real Pi compatibility yet. Prepared for validation
after the current full-suite screen; no existing runner or Pi entrypoint changed.

## Prepared inherited-boundary probe

`scripts/probe_task_boundary_integration.py` invokes the actual wrapper in a
fresh disposable workspace with two owned listening sockets. It checks normal
workspace/private-temp writes, `/dev/null`, outside and symlink writes, allowed
and denied endpoint ports, and a child interpreter that first writes inside
then attempts outside. External canary checks guard against false positives.
Its source parses; execution is deferred until the active model suite ends.
The probe cleans up only its own generated temporary files and closes its own
sockets. It does not contact the inference endpoint or modify benchmark files.
