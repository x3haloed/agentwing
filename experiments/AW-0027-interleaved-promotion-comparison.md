# AW-0027 — Interleaved promotion comparison

## Hypothesis and frozen sequence

The retained candidate preserves verified success count and doubles verified
utility/hour in each of two full-suite pairs, C1 → A1 → C2 → A2. Each arm uses
the same eight Stage A tasks, independent verifiers, 900-second task timeout,
original Swiftlet 459b201 executable, Qwen3.6 8-bit qpack, Pi 0.84.4, internal
SSD, 0.5 GB expert cache, compact-shell prompt, bash tool and declared prefix
salvage. Both arms use AW-0024's scoped write/outbound policy.

Control: max192, hard n-gram size3, no retained call boundary.
Candidate: max512, n-gram0, retained complete call boundary.
Other sampling remains temperature0, presence0, frequency0.5, topK20, topP0.8,
minimum new tokens8, thinking disabled. No optional extensions are loaded.

The machine-readable plan pins execution inputs and common/arm environments.
Run each slot through `scripts/run_frozen_arm.py`, preserving its launch output
and recording the slot-to-run mapping. A common evidence root avoids putting
arm labels in task workspace paths. Separate server startup per suite; no
filesystem cache flush. Record thermal and host observations through the runner.
No compilation, payload hashing, runtime edits, or concurrent inference during
measurements. Documentation/evidence-only commits may occur between slots.

## Acceptance and stops

Require both pairs to pass `scripts/assess_stage_a_pair.py`, including candidate
success count >=3 and >= paired control, rate >=2x paired control and >=4.129230
utility/hour, pressure below4, swap growth <=1 GiB, identical permissions and
frozen suite. Independently verify ordering, identical arm identities, protocol
tests, loopback observations, and source/build reproduction. Preserve all failed
runs. Runner red-line stops remain active; interrupted/incomplete runs cannot
count as full-suite replications. Numeric historical screens are not promotion.

## Results and disposition

Frozen; pending measurements. No configuration promoted.

### C1 terminal result and observer-only amendment

C1 `20260905T010110Z` completed all eight tasks:3 accepted in6276 endpoint
seconds (1.7208413001912046 utility/hour). Passes01/06/07; timeouts02/03/04/05/08.
Task03's artifact passed but timed-out completion correctly earns0. Pressure1,
swap735.19MiB unchanged. All five terminal cancellation drains observed. Model
owner and runner terminated; port8080 was free before the next launch.
Summary SHA256:e69bf54474a32d022bc7f240b3751c540fa699ef1df42fca41a38e9b315470c0.

The original offline audit rejected tasks02/03/04 solely because a known
same-request rejection diagnostic follows their terminal generation metric.
Swiftlet main.swift lines538–567 confirms this ordering after stream completion.
`evidence/AW-0027-C1-audit-original.json` preserves that failure. The corrected
predicate permits only the three known post-generation diagnostics, scoped to
the terminal request ID; missing metrics, foreign IDs, new replay activity and
unknown lines reject. All13 Python tests pass, including positive/negative
boundary regressions. The corrected full evidence audit passes.

Plan v2 records this observer-only amendment and updated auditor/test hashes.
Original plan is preserved. No measured execution input or scoring rule changed;
C1 remains the first paired control. Use v2 for A1/C2/A2. No promotion yet.

### A1 terminal result and first pair

A1 `20260905T024837Z` completed8/8 in4559 endpoint seconds (4552 task
seconds),6.317174819039263 utility/hour. Pressure1, swap735.19MiB unchanged;
52 tool calls,8 failed calls,0 model errors/rejections/salvage. Full evidence
audit passes. Summary SHA256:
3255de40c2ae02eff2b56e74e95d66d8366fc2910a27a168a577882b2ccc4241.
`evidence/AW-0027-pair-1.json` passes all necessary first-pair gates:
3.670980478175038 times C1's verified utility/hour. Session76879 exited0,
runner34667/server34729 terminated, and port8080 was free before C2.
Disposition: retain unchanged for C2 → A2; one pair does not permit promotion.

### C2 terminal result

C2 `20260905T040519Z` completed3/8 in5582 endpoint seconds (5575 task
seconds),1.9347903977069152 utility/hour. Passes01/06/07; timeouts02/03/04/08;
task05 completed but failed verification. All failures score0. All four timeout
drains observed.49 tool calls,11 failed calls,1 model-error reply,2 rejected
outputs,6 declared prefix salvages. Pressure1; swap735.19→735.50MiB (0.31MiB).
The full evidence audit passes in `evidence/AW-0027-C2-audit.json`.
Summary SHA256:f3f1ad31d9dca4873e61f4f4c4326c37c1bc6687996139df6cdfc35cb150d1f6.
Session77088 exited0, runner57579/server57634 are gone and port8080 is free.
Retain this control and advance unchanged A2; no promotion before its full
result and second-pair assessment.

### A2 terminal result and second pair

A2 `20260905T053919Z` completed8/8 in4534 endpoint seconds (4529 task
seconds),6.352007057785619 utility/hour. Pressure1, swap735.50MiB unchanged;
52 tool calls,8 failed calls,0 model errors/rejections/salvage. Full evidence
audit passes in `evidence/AW-0027-A2-audit.json`. Summary SHA256:
a360003f859c2854d4715e7daf07858ff3e150485da42e0850a0417b8a3d64a5.
`evidence/AW-0027-pair-2.json` passes all second-pair metrics at
3.28304661079253 times C2's rate. Session56985 exited0; runner85350/server85411
are gone and port8080 is free. Both paired metrics now pass. Final promotion
requires the requirement audit and usable configuration/reproduction handoff.
