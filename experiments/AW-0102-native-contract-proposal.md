# AW-0102 — Reviewable native whole-system comparison proposal

## Status and hypothesis

Draft only; not active. Hypothesis: split the bundled matched-profile condition
into matched task/prompt/tool/permission/deadline/scoring and declared frozen
native sampling/reasoning/context/output policies while preserving every other
quality/resource/replication/25% gate. Static check before any full P1 campaign.

## Proposal and result

spec/p2-native-migration-proposal.json is a complete reviewable contract.
Promotion, capability evaluation and representation-screen objects are byte-value
identical to current P2 contract. Every other existing invariant is unchanged;
matched prompt/tools/permissions/task deadlines/scoring explicitly retained.
Only model-native generation/context/output differences are proposed as part
of the complete experimental subject. Preserving P1 and native Bonsai settings
cannot meet the old matched sampling requirement (AW-0101).

The proposal changes no task/verifier/timeouts/scoring, no current runtime or
running experiment, and makes no profile or candidate eligible for promotion.
Original spec/p2-acceptance.json remains unchanged and authoritative until the
contract choice is explicitly resolved. No new held-out exposure.

## Evidence and disposition

Static inline JSON equality/hash checks exit0; small receipt
 evidence/AW-0102-native-contract-proposal-check.json pins both contracts.
Document preparation is concurrent incidental host work during AW-0100,
not an inference/performance experiment; full falsifier wall still includes it.
Unresolved contract choice. Continue independent safe development falsifiers.
