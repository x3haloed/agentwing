# AW-0194: Stationary cache fixed expanded multi-file falsifier

Status: prepared and gated; inference unrun.

Preserve the previously exposed dev-multi-file task, verifier, system prompt,
8192 output cap, medium thinking sampling, 16K context, 1800-second task
budget and bounded bash permissions. The only candidate change from prior
cache diagnostics is the AW-0191 non-speculative stationary-codebook server.
No held-out task is selected, and no P1 comparison or promotion is implied.
The complete frozen capability evaluation remains required for the goal.

AW-0193 must finish both cache arms without host/protocol failures and its
stationary candidate must produce a complete native tool proposal before
this runner permits inference. Never waive that gate for length exhaustion,
timeout, partial arguments or provisional fixture success.

Plan: `evidence/AW-0194-development-plan-v2.json`.
Raw destination: `/Users/chad/Models/agentwing/evidence/AW-0194`.
Prepare: `python3 scripts/run_bonsai_stationary_multifile.py --freeze`.
Run after admission: `python3 scripts/run_bonsai_stationary_multifile.py`.
Independent audit: `python3 scripts/audit_bonsai_selected_development.py RUN`.
All task failures, calls, setup/verification overhead and raw hashes remain
charged and preserved. P1 remains frozen.
