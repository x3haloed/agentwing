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

Run one task against a separately started loopback endpoint:

```sh
./scripts/run-stage-a.sh --task 01-navigation
```

Raw transcripts and manifests default to
`/Users/chad/Models/agentwing/evidence/AW-0008/` and stay outside Git.
