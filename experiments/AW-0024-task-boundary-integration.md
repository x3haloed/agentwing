# AW-0024 — Task write/network boundary integration

## Status

Inherited-boundary and real Pi protocol gates passed; opt-in runner integration ready for a real-model gate.

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

## Validated integration — 2026-09-05

All eleven inherited-boundary checks pass, including child-process inheritance,
allowed workspace/private-temp writes, denied outside and symlink writes,
allowed owned endpoint, and denied connection to a different owned listener.
The real Pi shell fixture passes under the wrapper, preserving five ordered
read/search/edit/failure/recovery calls and the expected single failed call.
Both original Pi fixtures and eleven Python tests also pass. See
`evidence/AW-0024-inherited-boundary-probe.json` and
`evidence/AW-0024-protocol-validation.json` for hashes and retained raw logs.

`AGENTWING_TASK_BOUNDARY=1` now explicitly selects this runner policy; default
is unchanged. Manifests record the policy name and profile/wrapper hashes.
The pair assessor rejects differing permission policies or hashes. The wrapper
runs inside the existing process group, with fresh private Pi/tmp/cache state.
The new real Pi fixture has a bounded deadline and archives logs in a fresh
caller-selected directory. Earlier successful fixture evidence is preserved.

Next gate: run the unchanged AW-0019 candidate on `07-bounded-read` with this
policy. Require verified utility, valid tool pairing, recorded policy identity,
and host gates. Then freeze the same policy for both comparison arms. This
does not revise the historical unbounded-policy floor or its scoring.

## Real-model gate completed

Run `/Users/chad/Models/agentwing/evidence/AW-0024/20260905T004228Z` passed
`07-bounded-read` with utility 1 in 222 endpoint seconds (217 task seconds),
three successful calls, full continuation reuse, no model errors/rejections/
salvage, pressure1, and zero swap growth. Policy and wrapper hashes matched
the manifest, and private Pi model configuration matched the archived config.
The runner/server terminated and port8080 was released.

Summary SHA-256: `c436703cc32d93b09fa548da42b2e30b564981bc6f0ca7d907aab2dc90a13871`.
`evidence/AW-0024-real-model-audit.json` passes copied-workspace replay and all
recorded integrity/host checks. This is a compatibility gate, not a performance
comparison with the unrestricted task's 212 task seconds.

Disposition: retain this explicit write/outbound policy for both paired arms.
No default agent configuration is promoted until the replicated rate and
success-count gates and remaining reproduction checks pass.
