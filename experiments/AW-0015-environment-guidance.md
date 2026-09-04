# AW-0015 — Give the shell agent accurate environment facts

## Status

Complete; rejected after the development falsifier.

## Hypothesis

Appending generic Python/test-runner availability facts to the compact shell
prompt avoids wasted environment-recovery turns and enables a previously
timed-out coding task to finish within the existing budget.

## Configuration identities

- Control: `compact-shell`, as measured in AW-0008's audited full suite.
- Candidate: `environment-shell`, the same prompt plus this exact suffix:

> Environment: python3 and standard-library unittest are available; python and pytest are unavailable. Discover the project's test command from its files instead of assuming a test runner.

Only prompt content changes. The runner archives the exact prompt and hash in
both arms. No task answers, filenames, repair hints, or verifier details are
added to the prompt.

## Fixed conditions

M1/16 GB, internal SSD, pinned 8-bit Qwen artifact, Swiftlet `d7352d79`, pinned
Pi, shell-only tools, prefix salvage, 0.5 GB expert cache, greedy sampling,
192 output tokens, frozen Stage A v1.1 task and verifier, 900-second timeout,
loopback server, and unchanged tool permissions. Exact commit, OS, prompt hash,
swap/pressure, storage reserve, and thermal snapshots are recorded per run.

## Primary metric and acceptance rule

Development falsifier: `02-single-file-fix` must finish normally with verifier
utility 1 within the unchanged timeout, under host gates. If it fails, reject
this exact prompt arm for a full-suite campaign. Environment errors and tool
counts are diagnostic only. A pass admits further paired trials; one task
cannot establish a suite improvement or promote a default.

## Cheap falsifier

Verify the named executable/module availability, run the existing offline
verifier and process-integrity tests, then the one frozen task. The historical
control timed out at 923 endpoint seconds and scored zero; comparison to it
is non-interleaved and cannot establish a causal speedup.

## Commands

```sh
AGENTWING_TOOL_PROFILE=shell AGENTWING_SALVAGE_TOOL_PREFIX=1 \
  AGENTWING_PROMPT_PROFILE=environment-shell \
  AGENTWING_EVIDENCE_ROOT=/Users/chad/Models/agentwing/evidence/AW-0015 \
  ./scripts/run-aw-0008.sh --task 02-single-file-fix
```

## Results

Run `20260904T220831Z` scored zero after a 900-second task timeout. It executed
five tool calls without trying the missing `python`/`pytest` commands, but
produced a malformed function signature (`lower: int.upper: int`) and an
unbalanced return expression. One salvaged tool prefix forced an 890-token
refill taking 229.1 seconds TTFT. Environment guidance did not restore a
verified coding outcome.

Cancellation did not produce a terminal metric within the 30-second drain
window. AW-0014's guard therefore stopped the suite and shut down the server.
Total endpoint wall time was 939 seconds; pressure peaked at 1 and peak/final
swap growth was zero. No benchmark process remained. This is a failed
experiment with an unconfirmed drain, not a comparable completed-suite score.

## Confounders and deviations

The development task has been inspected and is not held out. The machine's
available commands are legitimate harness context, but their benefits must
still generalize across the frozen suite. The additional prompt tokens incur
prefill cost. System and filesystem caches are not flushed between runs.

## Evidence

`/Users/chad/Models/agentwing/evidence/AW-0015/20260904T220831Z`.
Summary SHA-256:
`18b66fcd22d94853bdabc3eecd999a1a20dc48aa3949aa18444e8a6f3d00d122`.
The run pins Agentwing `a984d9b` and Swiftlet `d7352d79`; the running binary
was not rebuilt or changed during this trial. Subsequent sampler-source edits
were prepared separately from the executing binary.

## Conclusion

The exact prompt arm fails its predeclared single-task gate. The hard-trigram
mechanism found in AW-0016 is a more direct next target than further prompt
wording changes.

## Disposition

Rejected for a full-suite campaign. Preserve the trace and failure evidence.
