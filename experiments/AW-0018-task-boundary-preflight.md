# AW-0018 — Native task-boundary preflight

## Status

Exploratory canary preflight complete; agent integration unproven.

## Hypothesis

The local OS can allow task-workspace writes and a declared loopback endpoint
while denying writes elsewhere, symlink escapes, and other outbound endpoints.

## Primary metric and acceptance rule

Integrity only: an allowed canary write and connection must succeed; outside
writes, a symlink escape, and a different port must receive an OS permission
denial. No outside file may be created. Use only disposable files and a socket
owned by the probe. This is not an endpoint timing experiment.

## Results

The first exploratory profile did not load: this OS's network filter rejects
numeric host strings and requires `localhost` or `*`. This syntax failure is
not evidence of confinement. Retrying with `localhost:<owned port>` passed all
five action checks and the canary-integrity check in the current environment.

```sh
python3 scripts/probe_task_boundary.py
```

The reusable probe and profile are committed with
`evidence/AW-0018-boundary-preflight.json`. The exploratory checks ran alongside
AW-0017 without sending any request to its inference server or changing its
configuration. They took less than a second and supply no throughput claim.

## Limits and disposition

Retained as a preflight only. The profile allows reads and other capabilities
by default; it is not a comprehensive adversarial sandbox. Pi's state writes,
child processes, temporary files, platform services, and complete real coding
paths have not been integrated or validated. No benchmark tool permissions
were changed. Apply any eventual production policy to both comparison arms
and record the policy explicitly before claiming a causal performance result.
