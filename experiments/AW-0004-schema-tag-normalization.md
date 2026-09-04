# AW-0004 — Explicit schema-tag tool normalization

## Status

Ready to run.

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

Pending.

## Disposition

Unresolved.
