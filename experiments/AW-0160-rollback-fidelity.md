# AW-0160 — forced rejected-draft rollback fidelity

## Hypothesis and primary gate

Bounded recurrent rollback restores accepted-history state after1/2/3 rejected
speculative draft tokens. Predeclare full-vocabulary next-token relativeL2<=.001,
identical top1 and top20 set, all finite. This raw API diagnostic does not test
sampler clone/grammar/server protocol or end-to-end utility.

## Configuration and procedure

Isolated AW158 full runtime/library build, selective Bonsai model,16K context,
q8K/Turbo4V, n_rs_seq3, batch/microbatch128. Native PTQ multicol enabled for both
arms; fixture function/compiled binary and real AW1481186-token prefix plus
AW154 generated IDs hashed before launch. Whole model/runtime profile, M1/16GB /
macOS27.0.1/internalSSD/thermal/cache state pinned in external execution plan.
No weight/profile/default/P1 or task/harness/sampling/scoring changes.

Six fresh sequential contexts share one loaded model. For accepted counts0/1/2,
control decodes authoritative IDs sequentially through the correction token.
Candidate decodes current token +three drafts, replacing rejected future IDs
with deterministic wrong IDs, removes rejected positions, then decodes the same
correction token. Final histories match; compare full248320-logit rows. This
also includes batched-versus-single-token numerical effects. No model-generated
sampling claim. One owner lock; pressure<4/growth<=1024MiB,180s watchdog.

Commands: python3 scripts/run_bonsai_rollback_fidelity.py then
python3 scripts/audit_bonsai_rollback_fidelity.py after terminal successful run.
Raw independent auditor replays hashes and every expected arm record/finite
full-vocabulary array; predeclared gate unchanged.

## Evidence and disposition

External frozen plans/native log/host samples/binaries/arrays:
/Users/chad/Models/agentwing/evidence/AW-0160.
Final outcome in small terminal receipt. Preserve failures and partial evidence.
Even a pass admits only early-prefix numeric rollback; later accumulated state,
sampler/server protocol, actual whole execution cost and endpoint are open.

## Terminal result

Fixed180s watchdog stops child exit-15 at180.131s. No timeout extension or
rescore. Four arms complete: rejection3 relativeL2.000280041 and rejection2
.000155294, both identical top1/top20. Rejection1 complete pair missing.
Independent auditor verifies raw hashes and finite248320-vocabulary arrays,
reports host pass but overall execution/fidelity fail (incomplete). Pressure1,
swap baseline1198.56MiB, growth0. Two partial numeric passes are retained.
Full six-context repeated prefill costs are charged to this diagnostic; no
endpoint speed or implementation correctness conclusion from the timeout.
Finish remaining case in a separately pinned run without changing the model /
context/proposer/numeric gate. Receipt evidence/AW-0160-rollback-fidelity-terminal.json.
