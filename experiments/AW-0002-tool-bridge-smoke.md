# AW-0002 — Native Swiftlet/Pi tool bridge smoke

## Status

Ready to run.

## Hypothesis

The Agentwing Swiftlet patch can carry one Pi `read` call and its result through
Qwen3.6's native tool template without malformed markup, changed call identity,
or more than 1 GiB swap growth at a 0.5 GB expert-cache budget.

## Configuration identity

- Model: `Leonickson/Qwen3.6-35B-A3B-8bit-qpack` at
  `720a56073578a3b42b5c40410baf90281bab9c0f`
- Runtime base: Swiftlet at
  `694706e1d8ec67021f4350be88c912b3cb50cb32`
- Runtime patch commit: `793a9a18bc3ba8f5f1e06bd50415bf2373088daf`
- Patch artifact SHA-256:
  `9cc1c5b57ecf20e3f9eddc74801a20be5ea15f3e4b9b9b7b1fe4f651904add60`
- Harness: Pi 0.84.4 at
  `6aedd1066e540642165aa30fa7b4a1b863778aa7`
- Expert cache: 0.5 GB
- Concurrency: one
- Server: loopback port 8080
- Output cap: 96 tokens per model turn
- Tools: `read` only
- System prompt: short fixed protocol instruction
- Storage: internal SSD

## Cheap falsifiers already passed

- 24 focused tool-transport tests pass.
- Full Swiftlet suite passes: 169 tests in 28 suites.
- Release `swiftlet-server` builds.
- A tiny-model HTTP request with a function schema returns valid streamed Chat
  Completions framing and usage.

## Stop conditions

- Stop immediately if `kern.memorystatus_vm_pressure_level` reaches 4.
- Stop if allocated swap grows by more than 1,024 MiB from the pre-server
  sample.
- Stop on malformed tool output, undeclared tool selection, protocol error,
  timeout, or any second model-owning process.

## Fixture

In an isolated directory containing one `TARGET.md`, ask Pi to use `read`
exactly once and report the first Markdown heading. Preserve Pi and server logs
outside Git; commit only hashes and a compact result.

## Results

Pending.

## Disposition

Unresolved.
