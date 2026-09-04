# AW-0016 — Allow necessary repetition in generated code and tool calls

## Status

Frozen; tokenizer falsifier identified a hard sampler obstruction.

## Hypothesis

Disabling the greedy sampler's hard repeated-trigram ban permits necessary
literal, path, and protocol repetition, improving verified task completion
without requiring a larger model or token budget.

## Configuration identities

- Control: Swiftlet `d7352d79`, temperature 0, frequency penalty 0.5,
  presence penalty 0, hard no-repeat-ngram size 3.
- Candidate: explicit `--allow-repeated-ngrams` server arm, changing only
  no-repeat-ngram size to 0. Default behavior remains the control.

## Fixed conditions

Same pinned Qwen artifact, M1/16 GB, internal SSD, Pi, **compact-shell** prompt
(not AW-0015's environment prompt), shell-only tool, prefix salvage, 0.5 GB
expert cache, 192 generated tokens, 900-second task timeout, frozen Stage A
v1.1 verifier, loopback endpoint, and unchanged tool permissions. Preserve
all other sampling controls and token suppression. Hash prompt, manifest,
runtime patch, and traces. Build release server only after AW-0015 terminates.

## Primary metric and acceptance rule

First endpoint falsifier: `08-config-sync` must terminate normally with utility
1 under existing timeout and host gates. A pass admits `02-single-file-fix`
and then the full suite. A failure rejects promotion and requires inspecting
the exact failing mechanism before changing another variable. No single-task
result promotes a default; eventual promotion uses the active goal's two
interleaved full-suite comparisons.

## Cheap falsifier

Tokenize generic code/protocol fixtures with the pinned tokenizer and check
the actual hard-guard function against the required next token. The canonical
tokenization of `127.0.0.1` is `[16,17,22,13,15,13,15,13,16]`; the third period
is banned because `.0.` has already occurred. A repeated ordinary path and a
second tool-call block also require banned tokens. The typed-addition fixture
does not, serving as a negative comparison. A function with three typed integer
parameters does hit the ban on the second `: int,` sequence, showing how a
correct function signature can be disrupted before the body is generated.

This establishes a sampler obstruction for these ordinary tokenizations, not
that every alternative segmentation is impossible or that all errors came
from the guard. Frequency penalties and disabled reasoning remain possible
separate causes. Keep them unchanged for this arm.

## Commands

```sh
python3 scripts/analyze_ngram_guard.py
# After runtime validation and release build:
AGENTWING_TOOL_PROFILE=shell AGENTWING_SALVAGE_TOOL_PREFIX=1 \
  AGENTWING_PROMPT_PROFILE=compact-shell AGENTWING_ALLOW_REPEATED_NGRAMS=1 \
  AGENTWING_EVIDENCE_ROOT=/Users/chad/Models/agentwing/evidence/AW-0016 \
  ./scripts/run-aw-0008.sh --task 08-config-sync
```

## Results

The tokenizer-only fixtures reproduce the predicted bans. Model result pending.

## Confounders and deviations

The task has been inspected during development. The hypothesis originates in
the runtime sampler and generic fixtures, not a prompt containing task answers.
Removing a loop guard could produce genuine repetition loops; timeouts and
parser rejection remain enforced and every failed generation stays in evidence.
The upstream motivation is documented in
[Swiftlet issue 13](https://github.com/leonickson1/Swiftlet/issues/13): short
coding prompts reportedly repeated on quantized containers. That report explains
why a control exists; it does not establish that a hard trigram ban is suitable
for this pinned agent system.

## Evidence

`evidence/AW-0016-ngram-obstruction.json`; external endpoint trace pending.

## Conclusion

Pending endpoint evidence.

## Disposition

Unresolved.
