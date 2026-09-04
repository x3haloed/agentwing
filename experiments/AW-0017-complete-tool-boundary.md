# AW-0017 — Stop after a complete tool call while retaining exact state

## Status

Frozen for implementation; endpoint trial follows AW-0016 termination.

## Hypothesis

Ending each tool response at the first complete closing tag avoids generating
a partial second call at the 192-token cap and preserves exact prefix reuse,
improving verified work rate over the no-hard-trigram-ban arm.

## Configuration identities

- Control: AW-0016, repeated n-grams allowed, otherwise original compact-shell
  configuration.
- Candidate: explicit `--stop-after-tool-call` in addition, with a retained
  `</tool_call>` boundary. Stop only after the closing token has been fed into
  the model; retain all emitted bytes, including any trailing whitespace in
  that token. The normal strict parser still authorizes the completed call.

## Fixed conditions

Pinned Qwen qpack, M1/16 GB, internal SSD, Pi, compact-shell prompt, shell-only
tool, explicit salvage policy, 0.5 GB expert cache, temperature 0, presence
penalty 0, frequency penalty 0.5, 192 output tokens, no hard n-gram ban,
900-second timeout, frozen Stage A v1.1, loopback inference, and unchanged
tool permissions. Do not run a build or another model during endpoint timing.

## Primary metric and acceptance rule

First endpoint falsifier: `08-config-sync` must finish normally with verifier
utility 1 under the fixed timeout and safety gates. All post-tool requests
must reuse their complete cached prefix; no malformed-suffix salvage should
be needed. A pass admits a coding task and a full-suite candidate screen.
Only the active goal's full interleaved comparisons can promote a default.

## Cheap falsifier

Use a deterministic model to emit a tool-call delimiter across token pieces,
including a case where the final token also carries whitespace. Verify the
closing token is emitted and consumed, no following token is generated, and
the next rendered tool-result prompt reuses the same model state with only
its new suffix evaluated. Verify default behavior and requests without tools
remain unchanged. Run all Swift and Pi protocol tests before real inference.

## Commands

```sh
AGENTWING_TOOL_PROFILE=shell AGENTWING_SALVAGE_TOOL_PREFIX=1 \
  AGENTWING_PROMPT_PROFILE=compact-shell AGENTWING_ALLOW_REPEATED_NGRAMS=1 \
  AGENTWING_STOP_AFTER_TOOL_CALL=1 \
  AGENTWING_EVIDENCE_ROOT=/Users/chad/Models/agentwing/evidence/AW-0017 \
  ./scripts/run-aw-0008.sh --task 08-config-sync
```

## Results

Runtime `459b201` passes all 180 tests in 29 suites, including the retained
delimiter/state tests and unchanged default behavior. The release server
builds. Both Pi protocol fixtures pass, including shell failure/recovery and
streamed arguments. Six Python tests and the eight-pristine-task verifier
checks pass. Real endpoint measurement pending.

## Confounders and deviations

One call per response can increase round trips compared with native multi-call
responses; the tradeoff must be measured end to end. A closing tag inside
malformed text can terminate generation but still must fail the parser. This
is not permission to repair arguments, remove rejected history silently, or
weaken verifiers. This retained boundary is distinct from ordinary API stop
strings, which strip output and invalidate state reuse in the current runtime.

## Evidence

`evidence/AW-0017-validation.json` records test/build log and binary hashes.
Runtime change is exported as `patches/0009-Retain-complete-tool-boundaries.patch`.

## Conclusion

Pending.

## Disposition

Unresolved.
