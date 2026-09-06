# AW-0053 — Test whether a larger output budget completes the coherent test call

## Status and prerequisite

Conditional plan only. Do not build or launch during AW-0052 measurements.
Require terminal AW-0052 receipt/trace audit and both 0.5 controls reproducing
the cached reference before advancing. A1 has already produced a coherent but
incomplete 512-token call; this does not establish a successful repair.

## Hypothesis and primary metric

For the exact captured request input with zero frequency penalty, a 1024-token
output ceiling permits a complete, valid bash tool call containing useful
regression coverage. Completion must occur within the same 1800-second diagnostic
deadline, normal host gates and unchanged 0.5 GiB expert cache. The first 512
selected tokens and their observed scores must match AW-0052 A1, showing that
the extended ceiling did not change the already-observed prefix. If they differ,
retain the result but reject the intended controlled-continuation interpretation.

Primary diagnostic is complete protocol plus source-level validity of the
requested test artifact within the bound. A coherent partial response, absence
of loops, shorter output, test-process exit 0 or passing tests on manually
repaired text is insufficient. No endpoint utility is measured by this probe.

## Cheapest falsifier and fixed conditions

One model-only arm, no tool execution. This is not a throughput comparison;
the new arm itself must reproduce the entire old 512-token prefix before its
additional output can count as the tested continuation. Use AW-0052 A1 as the
pinned negative reference and the exact same 2219 captured input IDs. Keep
model, tokenizer, q8 representation, internal SSD, runtime generation logic,
cache/overlap settings, temperature 0, presence 0, frequency 0, no-repeat-ngram 0,
minNew 8, suppressed/EOS IDs and stop conditions unchanged. Change only requested
maxNew from 512 to 1024 in an isolated diagnostic probe. Verify admission returns
1024 before generation; do not raise the runtime context capacity.

The existing AW-0052 test hard-checks 512. Prepare a separate source/probe and
source/binary manifest after the prerequisite passes; preserve old binaries,
plans and traces. Launch the testing helper directly as the owned process-group
leader, with the already-validated pinned Testing framework path. Freeze all
identities before launch; no concurrent build or model. Pressure >=4, swap
growth >1024 MiB or deadline violation stops and preserves the attempt.

## Output review and interpretation

After model process termination, parse the complete response with the unchanged
runtime tool parser and original bash schema. Inspect commands without executing
them. Require a closed tool call, expected writable test artifact, syntactically
valid Python and regression assertions addressing requested behavior. Keep
validation of executable behavior separate: an optional later sandboxed copy
check must have its own explicit plan, provenance and costs; do not repair or
execute incomplete generated calls. Functionality still needs a full autonomous
task, including the pre-existing API Boolean-limit failure and any recovery.

If the call remains incomplete, repeats or is invalid at 1024, reject this exact
budget arm; do not keep raising caps in the same experiment. If it succeeds,
retain only as a candidate component for development endpoint testing. Do not
claim general capability from one saved prefix. Require broader tasks and all
original/held-out/replicated endpoint gates before promotion.

## Acceptance compatibility

This explicitly changes a diagnostic sampling budget and supplies no promotion
comparison. Frozen P1, benchmarks and P2 acceptance remain unchanged. Current P2
acceptance requires matched sampling/context/prompt across comparison arms;
a future end-to-end design involving changed sampling must explicitly resolve
that constraint while retaining the frozen P1 anchor, the >=25% target and all
capability/host/protocol/permission gates. Do not silently relabel a changed
sampler as frozen P1 or weaken criteria because this development case improves.

## Disposition

Unresolved conditional diagnostic; no model attempt or new candidate promotion.
