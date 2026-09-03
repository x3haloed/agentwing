# Project instructions for coding agents

Read `TARGET.md`, `RED_LINES.md`, `LEARNINGS.md`, and `docs/WORKFLOW.md` before
changing runtime, evaluation, model-adapter, or performance code.

## Required discipline

- Treat the complete model-runtime-harness configuration as the experimental
  subject. Do not attribute system results to the model alone.
- Optimize verified autonomous work per wall-clock hour. Tokens/s is a
  diagnostic, never the primary acceptance metric.
- Benchmark end to end. Kernel, storage, prefill, decode, tool-format, and
  verifier measurements are component evidence, not endpoint results.
- Record model revision, quantization, runtime commit, harness commit, prompt
  and skill revisions, context policy, sampling, storage device, cache state,
  thermal state, hardware, and OS for every performance claim.
- Record all attempted tool calls and distinguish valid, productive,
  redundant, malformed, denied, and failed calls.
- Reject runs with protocol corruption, unbounded resource growth, critical
  memory pressure, or swap growth beyond the declared gate.
- Never commit model weights, credentials, private repositories, raw licensed
  benchmark data, or large generated traces.
- Keep large evidence outside Git. Commit manifests, hashes, summaries, and
  small non-sensitive fixtures.
- Prefer a cheap falsification experiment before a large implementation or
  download.
- Give each experiment a stable `AW-NNNN` record under `experiments/`.
  Preserve negative and reversed results.
- Never silently change the task set, verifier, timeout, tool permissions, or
  scoring when comparing configurations.
- Use interleaved control/candidate runs when warm-up, page cache, storage,
  memory pressure, or thermals can bias order.

## Documentation contract

When an experiment changes a belief:

1. Add or update its `AW-NNNN` record.
2. Record raw-evidence hashes and the external evidence location.
3. Append the change to `LEARNINGS.md`; supersede old beliefs rather than
   deleting them.
4. Update machine-readable configuration or acceptance specs if warranted.
5. State whether the branch was promoted, retained as a control, rejected, or
   left unresolved.

