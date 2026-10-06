# AW-0192: Stationary cache multimodal functional admission

Status: running; unresolved. No endpoint promotion.

Test AW-0191's pinned full server, AW-0186 stationary Turbo4 V codebook,
Q8 K, selective attention PQ weights, and full Q8 vision projector in two
fresh-server replicas. Preserve the AW-0140 fixture, native medium thinking
sampling, 16K context, image limit, tool boundary, and host gates. Native
chat fixtures use a 768-token output cap; Pi retains its 8192-token cap.
These are functional checks, not the fixed capability benchmark or utility
comparison. P1 remains the frozen control.

Frozen plan: `evidence/AW-0192-multimodal-plan.json`, SHA256 `02f1a3297dfb221a9907a416e75bd976d24fe764260b90ae6b9ab804a7eaecab`.
Raw evidence: `/Users/chad/Models/agentwing/evidence/AW-0192/`.
Each replica records request/response, Pi transcript, server output,
thermal snapshot, one-second pressure/swap samples, elapsed wall time and
raw file hashes. Stop at the first failed gate. The independent auditor
replays text, opposite image colors, native tool association, exact file
copy, canonical Pi protocol and sampled host gates.

Run: `python3 scripts/probe_bonsai_stationary_local.py`.
Audit after both replicas finish:
`python3 scripts/audit_bonsai_stationary_admission.py`.

First replica launched 2026-10-06T16:13:36Z. Terminal receipts and raw
hashes remain pending; no functional acceptance claim is made yet.
