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
