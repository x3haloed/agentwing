# Red lines

## Host safety

- Do not continue a benchmark under critical memory pressure.
- Do not accept a run with more than 1 GiB sustained swap growth unless the
  experiment explicitly studies swapping and is isolated from endpoint claims.
- Do not run two model-owning processes concurrently during a baseline or
  control measurement.
- Do not delete Firewing weights or other user data to make room. Storage
  reclamation requires an explicit user decision.
- Do not expose unauthenticated local inference servers beyond loopback.

## Claim integrity

- Do not call a configuration faster because decode tokens/s increased while
  verified utility/hour decreased or remains unmeasured.
- Do not compare scores produced by different task sets or verifier revisions
  without labeling the comparison non-causal.
- Do not call a publisher model-card score a local endpoint result.
- Do not treat a successful chat response as proof of agent-tool compatibility.
- Do not silently repair malformed tool calls in one arm but not another.
- Do not exclude failures, timeouts, malformed calls, or setup overhead from an
  endpoint result unless the metric definition explicitly excludes them.
- Do not promote a configuration from a single unreplicated run.

## Data and licensing

- Never commit weights, tokens, credentials, or private task content.
- Record licenses and exact model revisions before acquisition.
- Keep benchmark contamination probes and held-out verifier details out of
  prompts and generated training/calibration data.

