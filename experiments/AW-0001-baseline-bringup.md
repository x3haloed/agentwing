# AW-0001 — Qwen3.6 8-bit Swiftlet/Pi baseline bring-up

## Status

Stopped after the first real-model pressure smoke crossed the conservative swap
growth boundary. Artifact, runtime, and harness bring-up succeeded. Native tool
transport and lower-cache follow-ups continue separately in AW-0002 and
AW-0004.

## Hypothesis

Swiftlet can serve Qwen3.6-35B-A3B 8-bit to Pi through a lossless observable
tool protocol on the base 16 GB M1 without critical memory pressure or more
than 1 GiB sustained swap growth.

## Configuration identity

- Model: `Leonickson/Qwen3.6-35B-A3B-8bit-qpack` at
  `720a56073578a3b42b5c40410baf90281bab9c0f`
- Runtime: Swiftlet at `694706e1d8ec67021f4350be88c912b3cb50cb32`
- Harness: Pi 0.84.4 at
  `6aedd1066e540642165aa30fa7b4a1b863778aa7`
- Adapter: none; lossless native Swiftlet tool transport is required next
- Expert cache: 2 GB initially
- Concurrency: one
- Storage: internal SSD preferred; external SSD is a separately named arm

## Cheap falsifier

Before downloading weights, verify from source or a tiny protocol fixture that
the chosen adapter can round-trip Pi's tool declarations and results through
Swiftlet's Chat Completions interface without silently repairing calls.

## Stage A — protocol fixture

The agent must:

1. read a file;
2. search for a symbol;
3. apply a bounded edit;
4. run a test that initially fails;
5. interpret the failure and repair the edit;
6. stop after the verifier passes.

Reject malformed tool IDs, arguments, result association, or turn history.

## Stage B — pressure fixture

Run repeated tool turns for 30 minutes while recording memory pressure, process
memory, swap, storage reads, prefill, decode, and tool timing. Reject crashes,
critical pressure, protocol corruption, or sustained swap growth above 1 GiB.

## Results

- Artifact integrity: 50/50 files matched the downloaded `hashes.json`; hash
  manifest SHA-256 is
  `53f0b270042bea31e978543a2394f575df7193a5b8e85ab243686d8e3cfffbbf`.
- Swiftlet verification: 162 tests across 28 suites passed. Release products
  `swiftlet` and `swiftlet-server` built successfully with warnings.
- Pi isolation: 0.84.4 installed with lifecycle scripts disabled. The custom
  provider loads from an isolated Agentwing state directory.
- Pi protocol fixture: PASS. Pi declared `read`, preserved the fixture's call
  ID, executed the read, associated the result with the same ID, and continued.
- Stock Swiftlet protocol inspection: FAIL for agent use. `ChatRequest` ignores
  `tools`; message decoding drops `tool_calls`; responses expose text deltas
  only. The bundled model template and pinned tokenizer do support tool specs,
  so this is a tractable runtime boundary rather than a model limitation.
- Real-model smoke: 21-token prefill in 7.362 s; 16-token decode in 8.6 s at
  1.87 tok/s; 2 GB expert cache; 29% cache hit rate; 22.30 s process wall time.
  Maximum RSS was 2,593,275,904 bytes and reported peak memory footprint was
  4,412,750,016 bytes.
- Host pressure: memory-free estimate moved from 51% to 33%; swap moved from
  2,044.94 MiB to 3,659.88 MiB, a 1,614.94 MiB increase. No 30-minute run was
  attempted after this conservative stop trigger.

Compact evidence: `evidence/AW-0001-smoke-2026-09-03.json`.

## Disposition

Unresolved overall. The exact 2 GB-cache arm is not acceptable as a baseline
under the observed ambient host state. Retain the model/runtime candidate for a
separately named lower-cache or clean-state arm; do not infer a sustained
30-minute swap rate from one pre/post sample.
