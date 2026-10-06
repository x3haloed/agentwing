# AW-0216 — Accumulated trajectory localization

Post-run preserved AW215 log analysis: six requests launch, five release.
Sixth task727 starts at elapsed188.535569s and last recorded generation at
1804.540805s:1616.005236s,6832generated/1360remainingtokens. No executable
sixth call. Dominant failed wall time is accumulated generation, not startup
or repeated execution. No causal cache/speed or endpoint claim.
Receipt `evidence/AW-0216-trajectory-localization.json` hashes externalraw.
Initial timestamp parser wrongly assumed three fields; corrected to four,
with six-launch/five-release assertions. Raw unchanged.
Retain diagnosis for exact-request reconstruction before another model run;
full task/reasoning/deadline/verifier/permissions and P1 gates unchanged.
