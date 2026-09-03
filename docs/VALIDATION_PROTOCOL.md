# Validation protocol

## Primary metric

```text
verified_utility_per_hour = 3600 * sum(task_utility) / sum(wall_seconds)
```

Report passes/hour beside it. Task utility must be computed by a versioned
verifier that does not depend on the model's self-report.

## Required diagnostic metrics

- pass rate and partial utility
- end-to-end wall time
- time to first useful tool action
- prefill and decode throughput
- total tokens and tokens per passed task
- valid, malformed, redundant, failed, and productive tool calls
- peak resident memory and swap delta
- memory-pressure state and thermal state
- physical bytes read when available
- cold/warm application and filesystem-cache state

## Stage 0 — integrity

A candidate must complete a deterministic tool-loop fixture containing file
read, search, edit, shell execution, a failed command, recovery, and a verifier.
The transcript must preserve tool IDs, arguments, results, and ordering.

## Stage 1 — pressure

Run a 30-minute repeated-turn workload. Reject an endpoint configuration if it
crashes, corrupts protocol, reaches critical memory pressure, or grows swap by
more than 1 GiB. Record the exact context and cache state.

## Stage 2 — screening suite

Use at least 20 held-out tasks spanning bug repair, repository navigation,
refactoring, shell/data work, injected tool failures, and multi-file evidence.
Run three seeded trials per task. Keep task timeouts identical across arms.

## Stage 3 — external validity

Use a pinned public benchmark such as a Terminal-Bench 2.0 subset or
SWE-bench Verified milestone run. Preserve the public harness contract or state
every deviation.

## Comparison rules

- Interleave control and candidate order.
- Separate cold-start, warm-runtime, warm-prefix, and warm-filesystem results.
- Use the same task, verifier, timeout, permissions, and scoring revision.
- Report median and tail latency, not only means.
- Require at least five replicated runs before promoting a default.
- Publish failures and negative results with the same prominence as wins.

