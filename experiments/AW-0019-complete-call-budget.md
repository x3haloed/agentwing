# AW-0019 — Allow longer complete calls within the task timeout

## Status

First development gate passed; single-file repair gate next.

## Hypothesis

A 512-token output limit, combined with the complete-tool-call boundary, lets
longer legitimate calls finish without length-induced parser errors while
short calls still stop promptly and retain exact prefix reuse.

## Configuration identities

- Control: AW-0017, 192 output tokens, no hard trigram ban, retained tool boundary.
- Candidate: identical configuration with 512 output tokens.

Only the output budget changes. The runner archives the exact Pi model config
and its hash. It does not change the frozen task, tests, verifier, or timeout.

## Fixed conditions

Swiftlet `459b201`, pinned Qwen qpack and Pi, M1/16 GB, internal SSD, compact-shell
prompt, shell-only tool, explicit salvage policy, 0.5 GB expert cache,
temperature 0, presence penalty 0, frequency penalty 0.5, no hard n-gram ban,
retained complete-call boundary, 900-second task timeout, loopback inference,
and unchanged tool permissions. No production sandbox is applied in this arm.

## Primary metric and acceptance rule

First development gate: `08-config-sync` must score utility 1 and end without
a model-error reply, rejected tool output, or salvage, preserving exact
continuation reuse and host gates. Then test `02-single-file-fix` before a
full-suite screen. A local development success does not promote a default;
the active goal still requires two interleaved full-suite comparisons.

## Cheap falsifier

Verify runner argument bounds, syntax, and the archived config value. The
runtime has already passed 180 Swift tests and both Pi protocol fixtures;
it is unchanged. Run the same one-task endpoint with the larger cap.

## Commands

```sh
AGENTWING_TOOL_PROFILE=shell AGENTWING_SALVAGE_TOOL_PREFIX=1 \
  AGENTWING_PROMPT_PROFILE=compact-shell AGENTWING_ALLOW_REPEATED_NGRAMS=1 \
  AGENTWING_STOP_AFTER_TOOL_CALL=1 AGENTWING_MAX_OUTPUT_TOKENS=512 \
  AGENTWING_EVIDENCE_ROOT=/Users/chad/Models/agentwing/evidence/AW-0019 \
  ./scripts/run-aw-0008.sh --task 08-config-sync
```

## Results

`08-config-sync` passed with utility 1 in 620 endpoint seconds (616 task
seconds). Seven tool calls included one failed compound discovery command,
followed by recovery and a passing test. All seven continuations reused their
full prefix. There were no model-error replies, rejected outputs, or salvage.
The formerly truncated discovery call completed at 287 tokens. Peak pressure
was 1 and swap growth zero. The server and runner terminated; the port closed.

This costs more than AW-0017's 409 seconds because that run ended prematurely
with a parser error; clean completion, rather than a speedup, is the result.
The first gate passes. The unchanged single-file repair gate remains pending.

## Confounders and deviations

More available tokens may allow unnecessary work or longer failure loops.
Keep their full cost and timeouts in the metric. Single-task comparisons here
are non-interleaved development evidence, not causal promotion measurements.

## Evidence

External run: `/Users/chad/Models/agentwing/evidence/AW-0019/20260904T225714Z`.
Agentwing at launch: `19c0b8a`; Swiftlet: `459b201`.
Summary SHA-256: `d1422f4eca97694edad6fcb8c87c053fb46fd346bcf6cf934e77802351f8770b`.
`evidence/AW-0019-first-task-audit.json` passes hashes, tool pairing, request
ownership, protected-test integrity, verifier replay on a copy, and host gates.

## Conclusion

The larger budget resolves the observed truncation without losing prefix reuse.
Broader task utility and replicated suite performance remain unproven.

## Disposition

Retained for the second development gate; no default promotion.
