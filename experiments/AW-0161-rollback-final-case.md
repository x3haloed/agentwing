# AW-0161 — remaining forced rollback numeric case

## Hypothesis and primary gate

After accepting two of three drafts, one rejected draft can be removed without
changing corrected-history logits beyond the AW160 gate. Same finite full-vocab
relativeL2<=.001, identical top1/top20. AW160 watchdog result preserved.
This completes a missing diagnostic case, not a narrower agent task/verifier.

## Configuration and execution

AW158 isolated full runtime, selective Bonsai model, q8K/Turbo4V,16Kcontext,
3rollback slots, batch/microbatch128, multicol enabled. Same real1186-token prefix
and authoritative generated IDs as AW160. Mechanical fixture change ONLY starts
accepted loop at2 instead of0. Original fixture retained; independent auditor
checks exact source derivation and prior receipt/source hashes. Full model /
runtime/host/OS/storage/thermal/cache pins frozen in external execution plan.
One owner, existing pressure/swap gates, separate180s watchdog. No sampler,
server protocol, late-context, performance or endpoint admission implied.

Commands: python3 scripts/run_bonsai_rollback_final_case.py then
python3 scripts/audit_bonsai_rollback_final_case.py after terminal.
Compile derived fixture with pinned full-runtime headers/libs as AW160.
No timeout extension, default/P1/profile/model/task/scoring changes.

## Evidence and disposition

External /Users/chad/Models/agentwing/evidence/AW-0161 contains frozen plan,
compiled binary/log/native evidence and full corrected-history logit arrays.
Independent audit seals numeric scope; final receipt records terminal result.
AW160 remains incomplete even if this separately frozen case passes.

## Terminal outcome and experimental launch path

Exit0 at83.471s diagnostic wall; pressure1/no swap growth baseline1198.56MiB.
One-token rejection relativeL2.000228832, identical top1/top20; independent
source-derivation/raw/input/harness/binary/numeric replay passes. Together with
AW160's two completed pairs this supplies all three EARLY-prefix numeric cases,
not full-server/sampler/late-context or endpoint evidence. AW160 remains timed
out; all costs preserved and no speed comparison attributed to these runs.

Experimental launcher: python3 scripts/bonsai_rollback_server.py --verify-only
passes complete artifact/weight/patch/build-receipt/banner pins. Constructed
command equals AW159 admitted command except verbose; environment explicitly
sets native PTQ multicol. python3 scripts/bonsai_rollback_server.py starts the
experimental full-vision endpoint under owner/pressure/swap gates. Separate
spec/bonsai-turbo-rollback-local.json preserves all operational/P1 defaults.
The launch profile remains endpoint-unqualified. Native build banner unknown
revision is expected for archive build; sealed source/patch hashes are authority.
Terminal receipt: evidence/AW-0161-rollback-final-case-terminal.json.
