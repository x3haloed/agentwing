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
  `d43b27f99bf1eb2c16c18c4600f4f7cff7afc0c1`.

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

Pending.

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
