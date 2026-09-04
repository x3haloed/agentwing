# AW-0007 — Exact-prefix reuse for tool continuations

## Status

Ready to run.

## Hypothesis

Replaying only an accepted model-native tool call and requiring an exact token
prefix can reduce the second-turn TTFT by at least 2× versus AW-0004, while
preserving the correct Pi `read` result and the existing host-safety envelope.

## Configuration identities

- Control: AW-0004 at Swiftlet `b33871230f51d3e3ec497eb2e6724fbf9557bb9d`.
- Candidate: identical configuration plus Swiftlet
  `d43b27f99bf1eb2c16c18c4600f4f7cff7afc0c1`. Diagnostic-only T3 adds
  `076234fdda30dffecce47c6154bf19f817604437`.

## Fixed conditions

- Host and OS: Macmini9,1, Apple M1, 16 GB unified memory; current macOS.
- Storage: internal SSD.
- Model: `Leonickson/Qwen3.6-35B-A3B-8bit-qpack` at
  `720a56073578a3b42b5c40410baf90281bab9c0f`.
- Harness: Pi 0.84.4 at `6aedd1066e540642165aa30fa7b4a1b863778aa7`.
- Task/verifier: identical `TARGET.md` first-heading read used by AW-0004.
- Cache and generation: 0.5 GB expert cache, greedy, 96-token cap.
- Tools: Pi `read` only; loopback server; schema-tag normalization enabled.

## Primary metric and acceptance rule

Second-turn TTFT. Accept the performance hypothesis at no more than 86.1 s
(2× faster than AW-0004's 172.2 s), provided Pi exits 0 with `# Target`, the
server reports a nonzero reused-token count, memory pressure remains below 4,
and swap growth remains at or below 1 GiB.

## Cheap falsifier

Unit tests require an exact rendered prefix to reuse the same decode-state
identity and verify that a changed structured call is not replayed. All 172
Swiftlet tests must pass before the real-model run.

## Commands

```sh
./scripts/run-aw-0007.sh
```

## Results

### T1 — malformed first turn

The model emitted `<path>…</parameters>` on the first turn. The bounded parser
rejected it before the prefix path could be exercised. Pi exited 1; pressure
peaked at 2 and swap growth was 0 MiB.

Evidence: `/Users/chad/Models/agentwing/evidence/AW-0007/20260904T054129Z`

- `server.log`: `d8253acf8ae7f3d1719cea0e0ee58a1332dcc8c8c9a7673e697e2b501434722d`
- `pi.log`: `3eb4863aeebe9f9dfe16472eef406eb36514c3a841c98b7a000599c152e0043e`
- `pressure.tsv`: `7c5ea9b6163c3dadfce0f933ae102bbe020a00bec232dabda77abde55f236243`

### T2 — correct endpoint, zero reuse

The endpoint completed correctly, but the candidate reported zero reused
tokens. The first turn processed 447 prompt tokens and generated a 24-token
strict-format call at 116.0 s TTFT and 2.05 tok/s. The second turn reprocessed
1,155 prompt tokens at 295.6 s TTFT and generated 12 tokens at 2.11 tok/s.
Pressure peaked at 2 and swap moved from 3,507.88 to 3,451.88 MiB (-56 MiB).

Evidence: `/Users/chad/Models/agentwing/evidence/AW-0007/20260904T054408Z`

- `server.log`: `04fbe5898c32ffe4b05dbf72d5d74ef32fde009980161868d98778e41ee37d08`
- `pi.log`: `caad13f75eae49ddd7f54b6645538e7d5d05f9b6e0ba9ac8191158ab3d8d8d57`
- `pressure.tsv`: `c69934aa684c5675dcb1b122f3e22b8646361d0216fbb4d8e834448f1c27e77d`

### T3 — content-safe diagnostic replication

Pending. This trial adds only replay hit/miss dimensions and longest-prefix
length; it does not log arguments or other prompt content.

## Confounders and deviations

Run order is not interleaved because the control evidence already exists.
Page-cache, thermal, and ambient system differences therefore limit causal
attribution; this arm is a cheap falsifier, not a promoted benchmark result.

## Evidence

Pending.

## Conclusion

Pending.

## Disposition

Unresolved.
