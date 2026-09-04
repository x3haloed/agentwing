# AW-0015 — Give the shell agent accurate environment facts

## Status

Frozen for the first development falsifier.

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

Pending.

## Confounders and deviations

The development task has been inspected and is not held out. The machine's
available commands are legitimate harness context, but their benefits must
still generalize across the frozen suite. The additional prompt tokens incur
prefill cost. System and filesystem caches are not flushed between runs.

## Evidence

Pending.

## Conclusion

Pending.

## Disposition

Unresolved.
