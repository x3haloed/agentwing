# AW-0071 — TurboQuant source and full KV byte-cost screen

Retained as an integration candidate, 2026-10-05. Source evidence only.

Prismwing PW20 rejected direct MiMo reuse because padded K256/V128 dispatch was
missing; PW21 corrected its oracle but rejected serial scheduling and retained
large synthetic quantized output errors. Reuse these cautions, not fidelity
claims. Bonsai observes K256/V256, so this particular shape mismatch differs.
All files in the Atomic source lock match revision074bf826e1b06005a51737d29387e36657f41bf7.
The pinned source contains matching Turbo2/3/4 vec attention specializations.
Source and lock identities, checks and costs: `evidence/AW-0071-turboquant-source-screen.json`.

Prismwing's compiled 128-value layouts are34/50/68bytes. At current full8K FP16
KV512MiB, logical packed Turbo2/3/4 payloads are68/100/136MiB without head-padding
cost. These omit rotation buffers, alignment and installation/transient costs;
none reduce the149.62MiB recurrent state, its saved checkpoints, or model weights.
Do not call stockq4 or this practical WHT/Lloyd-Max codec the complete Google
PolarQuant+QJL algorithm. No Bonsai build, accelerated execution or fidelity test
has occurred. Retain a minimal Prism-compatible port for real-activation and
accumulated behavior tests after cheap optional-state-cache controls. Do not
replace the pinned runtime with the older Atomic fork or claim zero loss.
