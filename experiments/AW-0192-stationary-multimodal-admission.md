# AW-0192: Stationary cache multimodal functional admission

Status: both replicas passed independent functional admission; retained as experimental candidate. No endpoint promotion.

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

## Terminal results

Replicas completed in 225.374 and 201.834 seconds. Both passed arithmetic,
opposite-color image ordering, native lookup selection/result association,
and Pi byte-exact file copy with canonical protocol/cleanup checks.
Peak pressure was 2 for both; swap growth was 760.69 and 0 MiB respectively.
The first swap increase remains charged; no claim of zero resource growth.
Nine tools were attempted, all valid and successful: eight productive, one
redundant second-replica MD5 check, none malformed, denied or failed.

Receipt: `evidence/AW-0192-stationary-admission.json` records plan, auditor,
canonical protocol, result and artifact hashes. Each external replica's
`sha256.json` records raw top-level evidence hashes. Fresh server launches
do not imply cold OS page cache or reset swap between replicas.

This establishes local text/vision/tool functionality, not long-context
behavior, capability equivalence or utility/hour. Next: gated AW-0193.
