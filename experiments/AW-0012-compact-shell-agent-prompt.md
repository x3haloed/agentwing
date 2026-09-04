# AW-0012 — Compact relative-path shell agent prompt

## Status

Complete.

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

The candidate passed `01-navigation` with utility 1 in 591 endpoint seconds
(6.09 utility/hour), improving on AW-0011's 746 seconds by 20.8%. It used five
successful shell calls versus AW-0011's seven calls including one failure.
There was one observable prefix salvage, no rejected outputs, pressure peaked
at 1, and swap did not grow.

The initial prompt was 480 tokens and TTFT was 124.4 seconds. Prefix salvage
still forced one 809-token refill at 205.3 seconds TTFT; later exact-prefix
continuations took 5.5–8.2 seconds plus their new suffixes. The model ignored
the relative-path preference but avoided AW-0011's corrupted validation call.

## Confounders and deviations

One non-interleaved run can screen a large effect but cannot support promotion.

## Evidence

Run `20260904T163908Z`: summary SHA-256
`d23f58635bc9f61086b3cddf2743f7cb9bcf2eb855d61f4aef034e337202f513`;
transcript SHA-256
`344c5cc546f62e8cc8a88d453b4a1c5fecb7746d445fec5102c7fbadc4e0b06e`.

## Conclusion

The prompt profile clears its screen and is the fastest verified Stage A
configuration so far. A full eight-task run is required to establish its floor.

## Disposition

Retained as the Stage A floor candidate; not promoted or replicated.
