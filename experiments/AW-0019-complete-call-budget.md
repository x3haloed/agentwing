# AW-0019 — Allow longer complete calls within the task timeout

## Status

Frozen for endpoint trial.

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

Pending.

## Confounders and deviations

More available tokens may allow unnecessary work or longer failure loops.
Keep their full cost and timeouts in the metric. Single-task comparisons here
are non-interleaved development evidence, not causal promotion measurements.

## Evidence

Pending.

## Conclusion

Pending.

## Disposition

Unresolved.
