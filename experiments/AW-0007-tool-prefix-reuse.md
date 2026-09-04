# AW-0007 — Exact-prefix reuse for tool continuations

## Status

Complete. Exact-prefix reuse worked, but the predeclared 2× TTFT threshold was
not met because the successful validation returned an unbounded tool result.

## Hypothesis

Replaying only an accepted model-native tool call and requiring an exact token
prefix can reduce the second-turn TTFT by at least 2× versus AW-0004, while
preserving the correct Pi `read` result and the existing host-safety envelope.

## Configuration identities

- Control: AW-0004 at Swiftlet `b33871230f51d3e3ec497eb2e6724fbf9557bb9d`.
- Candidate: identical configuration plus Swiftlet
  `d43b27f99bf1eb2c16c18c4600f4f7cff7afc0c1`. Diagnostic-only T3 adds
  `076234fdda30dffecce47c6154bf19f817604437`; T5 adds the token-boundary fix
  `0ac19fe4984faa7c02e58858653381e2390a2947`.

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

This trial added only replay hit/miss dimensions and longest-prefix length; it
did not log arguments or other prompt content. The first turn again emitted
`<path>…</parameters>` and failed closed before a continuation. Pressure peaked
at 2 and swap growth was 0 MiB.

Evidence: `/Users/chad/Models/agentwing/evidence/AW-0007/20260904T055415Z`

- `server.log`: `9856c5ccc4ebd9b06f7d18661a8dfcb43339045fd60339226e1339574b1494b1`
- `pi.log`: `3eb4863aeebe9f9dfe16472eef406eb36514c3a841c98b7a000599c152e0043e`
- `pressure.tsv`: `3bd3c1351559cc95308aafe68609589f19dd492a16d44a32f53c1454173ec3b8`

### T4 — replay hit, token-prefix miss

The replay identity matched exactly and the endpoint completed correctly, but
only 442 of the 481 cached tokens matched the re-rendered prompt. The second
turn therefore reprocessed 668 tokens at 171.8 s TTFT, with zero reuse. The
divergence was the empty-think boundary: the first prompt tokenized its closing
half separately, while full-history rendering tokenized the identical joined
text atomically. Pressure peaked at 2 and swap growth was 0 MiB.

Evidence: `/Users/chad/Models/agentwing/evidence/AW-0007/20260904T055658Z`

- `server.log`: `99818a28be085c0398221e79393d3a5ebedb06407ce843ed86a2a683888181a4`
- `pi.log`: `caad13f75eae49ddd7f54b6645538e7d5d05f9b6e0ba9ac8191158ab3d8d8d57`
- `pressure.tsv`: `23551377604f0f731dfb08ba6233696953670d9866832292f7005350df55de04`

### T5 — atomic non-thinking render

Swiftlet passed `enable_thinking=false` into the template before tokenization,
eliminating the separately encoded newline join. The model emitted the known
malformed `<path>…</parameters>` form on the first turn, so the parser rejected
the run before reuse. Pressure peaked at 1 and swap growth was 0 MiB.

Evidence: `/Users/chad/Models/agentwing/evidence/AW-0007/20260904T060430Z`

- `server.log`: `260503181d6570a5963ac07f165838669ba5858d1199382e56972616e53dae33`
- `pi.log`: `3eb4863aeebe9f9dfe16472eef406eb36514c3a841c98b7a000599c152e0043e`
- `pressure.tsv`: `e790bed7df97ef53a51e9a77809be759993d69a5ea2b4e0ef6579922178b9504`

### T6 — exact-prefix reuse succeeds

The first turn made a valid strict call without a line limit: 445 prompt
tokens, 24 generated tokens, 114.0 s TTFT, and 2.02 tok/s. Replay identity hit,
and the second turn matched and reused all 469 cached tokens. It processed only
the 684-token full-file result, then generated the correct 12-token answer at
171.9 s TTFT and 1.99 tok/s. Pi exited 0 with `# Target`.

Pressure peaked at 2. Swap moved from 3,427.88 to 3,419.88 MiB (-8 MiB).

Evidence: `/Users/chad/Models/agentwing/evidence/AW-0007/20260904T060717Z`

- `server.log`: `101e8ad58e9623165fdf6db6aedeae059329fd9b1eacf38eeec38a6ed8f5d43a`
- `pi.log`: `caad13f75eae49ddd7f54b6645538e7d5d05f9b6e0ba9ac8191158ab3d8d8d57`
- `pressure.tsv`: `423342ef95eeaa05a54fc3dccbcb59491013104bf9dd38ed9a3203163a22275c`

## Confounders and deviations

Run order is not interleaved because the control evidence already exists.
Page-cache, thermal, and ambient system differences therefore limit causal
attribution; this arm is a cheap falsifier, not a promoted benchmark result.
The accepted control call requested 20 lines, whereas T6 omitted `limit` and
returned all of `TARGET.md`; the primary TTFT comparison is therefore
confounded by a 684-token new suffix. T2 is a closer full-file diagnostic: it
processed 1,155 tokens without reuse at 295.6 s TTFT.

## Evidence

Raw locations and hashes are recorded with each trial above. No model weights
or large traces are committed.

## Conclusion

Exact-prefix reuse is operational and saved 469 tokens. Against the
non-interleaved full-file T2 diagnostic, second-turn TTFT decreased from 295.6
to 171.9 s (1.72×), but the predeclared 86.1 s acceptance threshold was not
met. The remaining 684-token tool result dominated prefill, so bounded tool
output and history compaction are now higher-leverage than further prefix work.

## Disposition

Retained as a tested prototype; not promoted from this non-interleaved,
confounded run.
