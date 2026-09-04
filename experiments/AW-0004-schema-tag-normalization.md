# AW-0004 — Explicit schema-tag tool normalization

## Status

Complete. The schema-bounded normalization arm completed one end-to-end Pi
`read` loop without crossing a host-pressure stop.

## Hypothesis

An explicit parser arm that accepts `<path>…</path>` only when `path` is a
declared property of the selected function can recover Qwen3.6's repeatable
alternate syntax and complete the Pi `read` loop without accepting undeclared
arguments, mismatched tags, or more than 1 GiB swap growth.

## Configuration identity

Same model, Pi harness, task, 0.5 GB cache, greedy sampling, and 96-token cap as
AW-0002 T3. Runtime adds patch commit
`b33871230f51d3e3ec497eb2e6724fbf9557bb9d` and server flag
`--accept-schema-tags`.

Patch artifact SHA-256:
`c17c998b4fbe96526a7f6abdac0027b39a59282480e609fdacf5395c857a0dbd`.

## Normalization contract

- Strict Qwen `<parameter=name>…</parameter>` remains accepted.
- Alternate `<name>…</name>` is accepted only inside a complete declared
  function call and only when `name` exists in that function's JSON schema.
- Mismatched, overlapping, duplicate, undeclared, or trailing markup fails.
- Every accepted alternate tag is logged and counted as normalization.
- Results are a separate arm and cannot be reported as strict tool accuracy.

## Stop conditions

Identical to AW-0002.

## Results

- UTC interval: 2026-09-04 03:45:11 through 03:50:30.
- Result: completed; Pi exited 0 and reported `# Target` as the first Markdown
  heading in `TARGET.md`.
- First model turn: 446 prompt tokens, 35 generated tokens, 115.8 s TTFT, and
  2.13 decode tok/s. The declared `path` schema-property tag was normalized and
  logged before Pi executed `read`.
- Second model turn: 670 prompt tokens, 12 generated tokens, 172.2 s TTFT, and
  1.97 decode tok/s. No normalization was needed for the final text response.
- Pressure: all 63 samples were level 1. Swap remained exactly 3,547.88 MiB,
  for 0 MiB growth over the run.
- Raw evidence directory:
  `/Users/chad/Models/agentwing/evidence/AW-0004/20260904T034511Z`
- SHA-256:
  - `server.log`: `e9b938fecf8546c2b55f942e06ecde3997bae5bc3ed4aeb93464227fc0ad8569`
  - `pi.log`: `caad13f75eae49ddd7f54b6645538e7d5d05f9b6e0ba9ac8191158ab3d8d8d57`
  - `pressure.tsv`: `59e0a704b791568945ad40e163889fe3dc7ecf6d1ec52ca6090c0707c1023310`

## Disposition

Retain for broader Stage A testing. This single read task establishes protocol
viability, not tool-call reliability or verified utility. Repeated-turn prefill
is the immediate bottleneck: TTFT rose from 115.8 s to 172.2 s when prompt
history grew from 446 to 670 tokens.
