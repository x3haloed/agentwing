# AW-0047 — Combine validated replay retention and bounded expert streaming

Status: joint release build and 57 tests in 11 suites pass; development plan
frozen, agent comparison pending. No utility or promotion claim.

Combine AW-0046 a48dfbc (streaming, failed-fill cleanup and diagnostics) with
AW-0045 0843311 (bounded accepted tool-history spellings) in a fresh isolated
checkout. These touch different runtime paths. Preserve both prior branches and
P1. Run the combined protocol/cache/scheduling tests, including the real tokenizer
and 161-expert recovery, before a tool-driven development comparison. Keep full
model diagnostic tests explicitly selected so they cannot run accidentally with
ordinary unit checks.

Candidate enables expert overlap, chunk overlap, full-chain overlap, oversized
union streaming and historical tool replay. Keep the original 0.5 GiB cache,
normal chunk policy, Pi environment, task corpus, tools, permission boundary,
prompt, generation settings and scoring. New runner/profile artifacts must not
modify the frozen AW-0044 plan. Before another expensive agent run, pin the joint
source/binary/kernel, plan and runner; declare selected development task(s), order
and timeout. No held-out tuning or promotion from component results.

Expected mechanism: overlap read/compute, safely support larger routed unions,
and avoid token-history rewrites that trigger redundant full prefill. Charge
history lookup/storage, eviction fallbacks, additional command submissions,
cache effects, failures and complete task wall. Full agent behavior and the
>=25% verified utility goal remain unproven; zero-utility elapsed-time savings
cannot qualify this candidate.

Development order declared before outcomes: `dev-recovery` C1/A1/C2, then
`dev-multi-file` C1/A1/C2. Each arm uses a fresh server and workspace with the
existing 1800-second task timeout plus 60-second startup cap. Both tasks are
existing frozen development items; prompts/inputs/graders are unchanged. Record
every attempted arm and stop the remaining comparison on a host/protocol failure
before any further candidate change. A failed task score alone remains a result,
not a reason to change scoring or selectively discard the arm. `run_joint_development.py`
is derived from the pinned AW-0044 runner, changing only its evidence destination,
self snapshot name and allowlist to admit the two newly validated runtime flags.
Static admission still precedes the diagnostic clock; this is not the final
promotion accounting runner. Pin its hash and joint profile before C1 starts.

Joint runtime `4dff62e867d62288d4224974c4add523dad50437` reconstructs from AW-0043
plus the archived patch to tree `d325b9d190ed0b9f2587d485d745b4f922ae9963`.
The real tokenizer and 161-expert recovery tests pass in the combined build.
`evidence/AW-0047-build-and-tests.json` records build/source hashes;
`spec/joint-development-candidate.json` pins server, kernel and all five flags;
`evidence/AW-0047-development-plan.json` freezes the runner/order/corpus before
outcomes. Candidate admission and all 215 frozen corpus files pass checks.

Recovery C1 (P1) started at
`/Users/chad/Models/agentwing/evidence/AW-0047/20260906T091156.920519Z`.
Resume its live process rather than restarting. After completion, audit its
receipt/grade with `audit_p2_development.py`; check protocol and host gates before
starting A1 under the frozen stop policy. `scripts/audit_joint_development.py`
audits each completed three-arm case with `--task`, preserving zero rates and
explicitly distinguishing elapsed time from utility. Its CLI parses; actual
three-arm audit awaits the runs. Candidate plan and runner remain unchanged.

Recovery C1 completes with utility 1 in 1415.473 seconds (23.59 minutes),
2.5433 verified utility/hour. All protocol gates pass; pressure 1 and zero swap
growth. It used 18 tool calls, two failures and three repeated-command occurrences.
The model initially introduced an invalid `unicodedata.casefold` call, investigated
it, switched to the string method, passed the maintained validator and completed
the required documentation. Independent grader replay/receipt audit passes in
`evidence/AW-0047-recovery-C1-audit.json`; detailed result is adjacent. This is a
successful expanded control task that the joint candidate must preserve. P1
preflight passes after cleanup. Proceed to the frozen recovery A1.
