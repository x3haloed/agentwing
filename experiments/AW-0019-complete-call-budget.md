# AW-0019 — Allow longer complete calls within the task timeout

## Status

Both development gates passed; unchanged full-suite screen next.

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

## Second development gate — 2026-09-04

`02-single-file-fix` passed with utility 1 in 641 endpoint seconds (635 task
seconds), seven calls, two failed calls (missing Python command and reproduced
failing tests), then a correct repair and passing tests. All seven continuations
reused their full prefix, with zero model errors/rejections/salvage. Pressure
peaked at 1 and swap growth was zero. No runner/server process remained.

External run: `/Users/chad/Models/agentwing/evidence/AW-0019/20260904T230812Z`.
Agentwing at launch: `fcc5a3c`; runtime unchanged at `459b201`.
Summary SHA-256: `4331ef3d70965f29d4879d6186580fb77bc049ed70f5f0d3271a597a32ec03df`.
`evidence/AW-0019-repair-task-audit.json` passes copied-workspace verification,
protected-test integrity, protocol pairing, hashes, and safety checks.

Both initial gates now pass. Proceed to the unchanged eight-task screen with
`--all` (required; the runner default is navigation only), preserving all failures and endpoint costs.
This screen is developmental; it is not one of the paired promotion replications.
Retain candidate provisionally; promotion remains unproven.

## Preserved launch error

Run `20260904T231929Z` omitted `--all` and selected only navigation.
The manifest check caught this before any tool call. The owned runner was
terminated, and its server exited; the terminal run recorded utility 0,
56 endpoint seconds, Pi exit 143, pressure 1, and zero swap growth.
This is an operator setup failure, not a completed full-suite measurement.
All artifacts are preserved at `/Users/chad/Models/agentwing/evidence/AW-0019/20260904T231929Z`.
Summary SHA-256: `6dc34753b441374b34877e5679ff3a7450d7d2f17a82e1b16266d7c6dd9fc6e3`.
