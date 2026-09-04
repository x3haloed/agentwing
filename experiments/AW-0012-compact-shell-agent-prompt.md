# AW-0012 — Compact relative-path shell agent prompt

## Status

In progress.

## Hypothesis

A short shell-oriented policy that requires relative paths, favors one bounded
action, suppresses pre-tool narration, and stops after validation will preserve
AW-0011 task success while reducing tool calls and endpoint wall time.

## Configuration identities

- Control: AW-0011 shell-only + prefix recovery + base agent prompt.
- Candidate: identical configuration with `compact-shell` prompt profile.

## Fixed conditions

- Stage A v1.1 task and verifier, Qwen artifact, Swiftlet runtime, Pi harness,
  0.5 GB cache, shell-only tool, prefix recovery, temperature, output limit,
  timeout, host, storage, permissions, and network policy: unchanged.
- Experimental variable: system prompt profile only.

## Primary metric and acceptance rule

Primary metric: verified utility per endpoint hour. On `01-navigation`, retain
utility 1 and improve the AW-0011 746-second endpoint time by at least 10%.
Tool calls and failed calls are required diagnostics.

## Cheap falsifier

One frozen `01-navigation` run.

## Commands

```sh
AGENTWING_TOOL_PROFILE=shell \
AGENTWING_SALVAGE_TOOL_PREFIX=1 \
AGENTWING_PROMPT_PROFILE=compact-shell \
  ./scripts/run-aw-0008.sh --task 01-navigation
```

## Results

Pending.

## Confounders and deviations

One non-interleaved run can screen a large effect but cannot support promotion.

## Evidence

Pending.

## Conclusion

Pending.

## Disposition

Unresolved.
