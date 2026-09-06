# AW-0056 — Six-bit midpoint expert fidelity falsifier

Predeclare one modified representation before execution: store each unsigned
source q8 code's high six bits; reconstruct `4 * code6 + 2`. Preserve the
original group64 BF16 scale and bias bytes. Pack four codes into three bytes.
Each expert occupies 2,555,904 bytes including metadata (156 16-KiB pages),
76.4706% of the original 3,342,336 bytes. No calibration or task-derived tuning.

Primary continuation gate is unchanged from AW-0038: maximum routed-mixture
relative L2 <=5% and maximum expert-down relative L2 <=10% across all 72 frozen
AW-0036 real-activation fixtures and 576 selected expert executions, compared
with authenticated AW-0037 original stages. Layers 0/20/39 and the coding,
arithmetic and structured trajectories all remain included. These source-route
fixtures do not prove uncommon-route coverage or candidate-accumulated behavior.

This cheap screen packs and independently unpacks each expert, checks every
code's round-trip and <=2 source-code error, and checks unchanged metadata.
It executes the expanded modified q8 through the original fast8, SwiGLU and
ordered mixture kernels. Independent scalar double projections must agree
within 1e-4; retain all outputs and hashes. This separates representation error
from a future direct-six-bit kernel's correctness. No direct kernel or whole
bank conversion is justified before this gate passes.

The candidate's storage ratio alone gives only about 1.094x under AW-0031's
36.6%-read-time Amdahl assumptions, even with free decoding and proportional
read savings. It cannot by itself justify the endpoint goal. A survivor needs
direct packed execution or a fully charged alternative, installed residency,
SSD/memory traffic, cache-capacity effects, compute and conversion accounting,
then uncommon routes, accumulated validation and full agent evaluation.
Do not multiply it into past overlap speedups as if independently measured.

Use the existing bounded native-fixture supervisor: one owned process group,
300-second deadline, pressure/swap gates, preflight, local model lock. Read q8
source bytes and hold packed and expanded buffers; elapsed time is diagnostic
cost, not compressed inference performance. Source/model/layout/kernel/compiler,
hardware/OS/thermal state and source/reference receipts are recorded per run.
No prompt, sampling, frozen P1, task, grader or permission changes. No model
rollout, held-out execution, promotion or agent utility claim.

Command: `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/probe_expert_sixbit.py`.

Status: frozen for the single numerical screen; failure rejects this exact form.
