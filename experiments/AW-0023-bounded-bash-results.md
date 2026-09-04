# AW-0023 — Explicit bounded bash-result delivery

## Status

Prepared, offline hook tests pass; real Pi fixture and endpoint trial pending.

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
