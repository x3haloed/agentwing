# Agentwing Stage A v1

This is a compact, deterministic pre-screen for local agent configurations. It
does not replace the 20-task held-out Stage 2 suite in
`docs/VALIDATION_PROTOCOL.md` and cannot by itself promote a default.

Each task receives only its `input/` directory and prompt. Verification runs
outside the agent workspace from the frozen `manifest.json`, so the model
cannot edit its success criterion. One task is worth one utility point.

Validate that all pristine tasks correctly fail:

```sh
./scripts/verify-stage-a.sh --self-test
```

Run the cheapest task through the self-contained B0 endpoint runner:

```sh
./scripts/run-aw-0008.sh --task 01-navigation
```

Run the full pre-screen with `--all`. The runner starts one loopback-only
Swiftlet process, preserves task workspaces and JSONL transcripts, samples
memory pressure and swap every five seconds, and stops at the project safety
gates. Sequential tasks share a warm runtime and static prompt prefix; that
cache state is part of the declared B0 Stage A configuration.

Raw transcripts and manifests default to
`/Users/chad/Models/agentwing/evidence/AW-0008/` and stay outside Git.
