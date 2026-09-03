# Architecture

## Measured system

```text
task + repository
        |
        v
agent harness ---- permissions / tool policy
        |
        v
protocol adapter or local API
        |
        v
model runtime ---- model artifact ---- SSD / expert cache
        |
        v
tool requests ---- shell / files / tests
        |
        v
independent verifier ---- utility score
```

The configuration identity includes every box in this diagram. Changing the
harness, tool schema, prompt, adapter, runtime, model artifact, context policy,
or verifier creates a new configuration.

## Telemetry boundary

Every rollout should produce a compact manifest containing:

- configuration and source revisions;
- task and verifier revisions;
- monotonic start/end timestamps;
- prompt, prefill, reasoning, visible-output, and cached token counts when
  available;
- tool-call timestamps, classifications, and exit status;
- periodic memory pressure, resident memory, swap, CPU/GPU, energy, and disk
  read samples;
- verifier output and final utility;
- hashes for external raw logs.

## Adapter rule

An adapter may translate wire formats but must not add hidden problem-solving
capability. Any repair, retry, schema coercion, context trimming, or synthetic
tool result must be observable and identical across compared runs unless it is
the experimental variable.

