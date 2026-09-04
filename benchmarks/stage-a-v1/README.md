# Agentwing Stage A v1.1

This is a compact, deterministic pre-screen for local agent configurations. It
does not replace the 20-task held-out Stage 2 suite in
`docs/VALIDATION_PROTOCOL.md` and cannot by itself promote a default.

Each task receives only its `input/` directory and prompt. Verification runs
outside the agent workspace from the frozen `manifest.json`, so the model
cannot edit its success criterion. One task is worth one utility point.

Version 1.1 corrects task 01's verifier to accept the requested integer with or
without a trailing newline. No task input or prompt changed. Earlier v1 model
runs are retained and may be explicitly rescored; new comparisons use v1.1.

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

The separately labeled AW-0009 recovery arm is enabled with
`AGENTWING_SALVAGE_TOOL_PREFIX=1`. Strict parsing remains the default.
The AW-0010 minimal-interface arm uses `AGENTWING_TOOL_PROFILE=shell`; the
default `full` profile exposes all seven Pi tools.
AW-0012 adds `AGENTWING_PROMPT_PROFILE=compact-shell`, which requires the shell
tool profile. The default prompt profile remains `base`.

Raw transcripts and manifests default to
`/Users/chad/Models/agentwing/evidence/AW-0008/` and stay outside Git.
