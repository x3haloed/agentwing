# AW-0047 — Combine validated replay retention and bounded expert streaming

Status: predeclared integration, not built or evaluated yet.

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
