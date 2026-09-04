# AW-0002 — Native Swiftlet/Pi tool bridge smoke

## Status

Complete. Three strict trials failed closed on malformed model output without
crossing a host-pressure stop.

## Hypothesis

The Agentwing Swiftlet patch can carry one Pi `read` call and its result through
Qwen3.6's native tool template without malformed markup, changed call identity,
or more than 1 GiB swap growth at a 0.5 GB expert-cache budget.

## Configuration identity

- Model: `Leonickson/Qwen3.6-35B-A3B-8bit-qpack` at
  `720a56073578a3b42b5c40410baf90281bab9c0f`
- Runtime base: Swiftlet at
  `694706e1d8ec67021f4350be88c912b3cb50cb32`
- Runtime patch commits: `793a9a18bc3ba8f5f1e06bd50415bf2373088daf`
  and diagnostic-only `97e7775ba22b40b1015a74f20011ef78ee99b855`
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

### T1 — strict bridge, 96-token output cap

- UTC interval: 2026-09-04 03:29:54 through 03:32:16
- Result: Pi exited 1 after Swiftlet rejected `unclosed parameter markup`.
- Protocol behavior: failed closed; the malformed call was neither repaired nor
  forwarded to Pi as executable work.
- Pressure: macOS pressure level peaked at 2 and returned to 1. Swap moved from
  3,579.88 MiB to 3,571.88 MiB (-8 MiB).
- Raw evidence directory:
  `/Users/chad/Models/agentwing/evidence/AW-0002/20260904T032954Z`
- SHA-256:
  - `server.log`: `4fc131af6a46f231570453c359963b8d28aa2f6e1972c29b1400fd7a4a8bf886`
  - `pi.log`: `3eb4863aeebe9f9dfe16472eef406eb36514c3a841c98b7a000599c152e0043e`
  - `pressure.tsv`: `90e9b9c06fb16868606ee3cc8f800ffd9d3a2af7d096d04e309e751624f166c2`

T1 does not distinguish a generation truncated by the output cap from another
malformation because rejected raw output was not logged. The diagnostic-only
second patch adds opt-in escaped raw-output logging after a rejection; normal
server operation remains content-silent.

### T2 — diagnostic replication, default sampling

- UTC interval: 2026-09-04 03:34:25 through 03:36:47
- Result: Pi exited 1 after Swiftlet rejected a complete but malformed call.
- Model output: the model correctly selected `read`, emitted a valid `limit`
  parameter, then emitted `<path>…</parameters>` instead of the required
  `<parameter=path>…</parameter>` pair.
- Generation: 447 prompt tokens; 116.1 s TTFT; 35 generated tokens at 2.12
  tok/s.
- Pressure: macOS pressure level peaked at 2 and returned to 1. Swap moved from
  3,571.88 MiB to 3,563.88 MiB (-8 MiB).
- Raw evidence directory:
  `/Users/chad/Models/agentwing/evidence/AW-0002/20260904T033425Z`
- SHA-256:
  - `server.log`: `b94744b0193d9bc37357c303fe7d03a5a386d5574512d254443c86687d9ff4f3`
  - `pi.log`: `3eb4863aeebe9f9dfe16472eef406eb36514c3a841c98b7a000599c152e0043e`
  - `pressure.tsv`: `3d13f8ebfa98384cdc2ce712098552395c65b25308bc7b736e10fc04a7a73313`

### T3 — declared greedy variant

T3 changed only model sampling to `temperature: 0`. The task, tool schema,
96-token cap, 0.5 GB cache, bridge, and safety monitor remained fixed.

- UTC interval: 2026-09-04 03:37:35 through 03:39:57
- Result: Pi exited 1 after Swiftlet rejected a complete malformed call.
- Model output: the model again selected `read` and emitted a valid `limit`
  parameter, then used undeclared XML argument syntax `<path>…</path>`.
- Generation: 446 prompt tokens; 116.4 s TTFT; 35 generated tokens at 2.06
  tok/s.
- Pressure: macOS pressure level peaked at 2 and returned to 1. Swap moved from
  3,563.88 MiB to 3,547.88 MiB (-16 MiB).
- Raw evidence directory:
  `/Users/chad/Models/agentwing/evidence/AW-0002/20260904T033735Z`
- SHA-256:
  - `server.log`: `81df3736d17b401e895940c7d6e88ba4e5014deb91e1d0907b8daa7f57d5e332`
  - `pi.log`: `3eb4863aeebe9f9dfe16472eef406eb36514c3a841c98b7a000599c152e0043e`
  - `pressure.tsv`: `39dbf53a8c1d8be77b43662cf612e32575131f509b1e56f571352114021ea082`

## Disposition

Rejected as a strict-parser baseline. Default sampling and greedy decoding both
produced complete but structurally invalid tool calls. The bridge behaved
correctly by failing closed, and the 0.5 GB cache passed this short pressure
screen. AW-0004 separately tests an explicit, logged schema-tag dialect; its
results must not be merged with this strict arm.
