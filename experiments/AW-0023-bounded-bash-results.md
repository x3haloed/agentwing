# AW-0023 — Explicit bounded bash-result delivery

## Status

Offline screen complete; this exact cap is deprioritized before real Pi integration.

## Hypothesis

Delivering at most 1,024 Unicode code points for an ordinary single-text bash
result will reduce new prompt processing enough to improve complete task rate,
while preserving useful first diagnostics, final summaries, and error status.

## Candidate

The opt-in `extensions/bounded-bash-result.js` uses Pi's `tool_result` hook.
Long single-text bash results become a 60/40 head/tail excerpt with an explicit
truncation marker included in the limit. The marker instructs targeted retrieval
for omitted content. The complete original text remains in transcript details,
along with its original length and cap. Existing details and `isError` remain.
Short outputs, other tools, multiple content blocks, and mixed media are untouched.
This is a bash text limit, not a general all-media or token-budget guarantee.

The pinned Pi OpenAI conversion extracts tool text from `content`, not details
(`packages/ai/src/api/openai-completions.ts`, tool-result conversion). A real
wire fixture must still prove details retention and bounded delivery together.
No tool arguments, call IDs, task files, verifier, permissions, or old history
are rewritten. The model first sees the bounded result, permitting later exact
prefix reuse without retroactively shortening its cached history.

## Cheap falsifiers and results

Two Node tests pass: a Unicode failure report preserves head/tail diagnostics,
original evidence, file-path details and error status within the 1,024 limit;
ordinary short output and unsupported result shapes remain unchanged.

Offline replay of the seven AW-0019 repair-task results truncates only one,
from 1,231 to 1,024 code points. Others stay byte-identical. See
`evidence/AW-0023-offline-result-limit.json` for source/transcript hashes and
per-call counts. The small reduction on this task is not a performance claim
and suggests the cwd-hint arm may have more potential here.

## Required next validation

After inference ends, run a real Pi shell fixture with an intentionally long
failed output followed by targeted recovery, and assert outgoing content bounds,
call/result pairing, original transcript details, unchanged error status, and
successful recovery. Freeze extension hash/config in runner metadata before an
endpoint trial. Keep the current AW-0019 full-suite screen unchanged.

For an endpoint screen, compare the completed full-suite output profile first;
select a task with material result overhead without changing its prompt or
verifier. Require preserved utility and at least 10% lower endpoint duration to
retain this exact limit. Record lost-diagnostic failures and extra retrieval
costs. Only replicated full-suite pairs can promote a configuration.

## Disposition

Prepared option, not loaded or promoted. Offline evidence is insufficient to
claim that bounded-result delivery has improved agent performance.

## Offline falsification — source-token accounting

`scripts/profile_tool_results.py` replays the actual extension hook over archived
messages, then tokenizes its original and bounded text with the pinned tokenizer.
Across the baseline's 47 tool results, only one changes, saving 12 tokens total.
The clean AW-0019 repair's seven results save 37 tokens. The marker itself has
cost, so character savings overstate token savings.

Evidence: `evidence/AW-0023-baseline-result-profile.json` and
`evidence/AW-0023-repair-result-profile.json`, including all transcript, extension,
and tokenizer hashes. No endpoint, prompt, or transcript was changed.

The repaired task's measured 326.4 seconds of reported TTFT over 1,219 new prompt
tokens gives an approximate 0.268 seconds/token diagnostic average. At that
average, 37 fewer tokens suggest about 10 seconds, or 1.55% of the 641-second
endpoint, before any recovery cost. This is a rough linear projection, not a
causal latency bound; task behavior and fixed overhead can change. It falls
well short of this arm's 10% screen threshold. The baseline savings are smaller.

Disposition: reject this exact 1,024-character arm as a priority for the current
short-task workload; retain source/evidence for possible longer-output workloads.
Do not spend a real-model trial unless the completed candidate suite exposes
materially larger outputs. More aggressive limits and other bounded-delivery
policies remain untested; the whole optimization family is not exhausted.
