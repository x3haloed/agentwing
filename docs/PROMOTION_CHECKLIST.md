# Local promotion evidence checklist

Status at 2026-09-05: pending second pair. This checklist does not promote a
configuration or change the frozen AW-0027 execution plan.

| Requirement | Evidence and final check | Current state |
| --- | --- | --- |
| Frozen eight-task benchmark and measured floor | Stage A manifest/verifiers; AW-0008 audited3/8,2.064615/hour | Recorded |
| First interleaved pair | AW-0027-pair-1.json; C1 then A1 launch receipts and raw manifests | Passed:3.67098x, A1 8/8 |
| Second interleaved pair | Terminal C2/A2 summaries, independent audits, pair checker | C2 audited; A2 live, first four tasks passed |
| Same arms and correct ordering | Compare all four manifests to frozen plan v2, original plan amendment, slot receipts and timestamps | Four-launch identity/order check passed; A2 terminal audit pending |
| Preserve success and double utility in each pair | Each candidate>=3 and>=control successes;>=2x its control and>=4.129230/hour | Pair1 passed; pair2 pending |
| Pressure, swap and one model owner | Complete pressure traces, summaries, owned-process cleanup, no concurrent benchmark model | Pair1 passed; second pair pending |
| Loopback only | Recorded bind plus observed listener127.0.0.1:8080 for each run | All four launch listeners observed |
| Observable valid protocol and scoped permissions | AW-0024 real Pi fixtures/canaries, runtime tests, per-run evidence audit; identical policy hashes | Fixtures recorded; final run audits pending |
| Runtime reproduction | AW-0026 clean build,180 tests/29 suites, exact source tree and patch reconstruction | Passed source/build reproduction; executable bytes differ |
| Installed model identity | AW-0026-model-payload-verification.json,50 matching payloads; pinned metadata and manifest | Verified before comparison |
| Named optimization families and failures | AW-0014–0025 records, local-model-inventory.json, KV source accounting | Recorded screening/deferred arms; promotion is the intended stopping branch |
| Capacity management | Run manifests/free-space measurements; preserve external raw evidence | Adequate capacity; no reclamation needed |
| Usable promoted configuration and reproduction instructions | Update README and machine-readable configuration after frozen measurements; document exact runtime, model, Pi, prompt, sampler, cache, permissions, launch and validation commands | Pending promotion gates |

Final procedure: finish unchanged A2, audit A2 and assess pair2. Inspect all four run identities/order and required protocol/reproduction
sources. Only then update the default/configuration documentation and record a
requirement-by-requirement final promotion report. Run appropriate validation
for any new launch path. Do not modify frozen execution files during C2/A2.

The clean executable is not bit-identical to the measured original executable;
all paired runs must retain the original pinned binary. Keep this limitation
explicit. Stage A local promotion does not establish held-out or external
benchmark performance. Deferred optional families need not be exhausted if the
user's promotion stopping condition is satisfied.

Handoff review while A2 runs: `config/pi-models.json` is the generic bring-up
profile (32,768 output tokens), and `scripts/pi.sh` only starts Pi. Neither is
the measured candidate launch path. AW-0027 generates a per-run models file
with 512 output tokens and temperature zero, then runs Pi inside the task
boundary with the compact-shell prompt and an owned Swiftlet server. The final
handoff must provide the exact tested launch/settings and distinguish a full
benchmark reproduction from use on a new workspace. Any new general-task
launcher needs its own lifecycle/permission validation; the generic profile
must not be described as the promoted configuration. The advertised 262,144
context window is metadata, not a tested local context capacity.
