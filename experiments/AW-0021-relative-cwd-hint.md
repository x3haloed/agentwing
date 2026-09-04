# AW-0021 — Relative working-directory hint

## Status

Prepared, opt-in extension only. Not integrated into the runner or measured.

## Hypothesis

Replacing Pi's appended absolute working-directory hint with `.` will reduce
repeated absolute paths in generated commands and tool outputs, improving
verified endpoint utility/hour without changing tools, task contents, or cwd.

## Evidence motivating the arm

AW-0012's relative-path instruction was ignored. AW-0019's completed config
trial repeated its long workspace prefix eight times in seven commands.
Canonical tokenization of those command strings versus replacing only the
workspace prefix with relative paths yields 337 fewer command tokens. This is
potential overhead, not a measured speedup or a claim of equivalent generation.
The pinned Pi source appends the absolute cwd after the custom system prompt.

## Candidate and control

Control: AW-0019's 512-token compact-shell configuration. Candidate: identical
with explicitly loaded `extensions/relative-cwd.js`. The extension uses Pi's
`before_agent_start` hook and replaces only the exact final cwd suffix matching
the real context cwd. It leaves unmatched prompts unchanged. It does not rewrite
tool arguments/results/history, change working directories, or alter permissions.

## Cheap falsifier and acceptance

After the current inference run terminates, use the real Pi shell protocol
fixture to verify the outgoing system message contains the relative hint and
that all tool calls, results, and failure recovery still pass. Archive source
hash and extension setting in the runner before endpoint measurement. Then
require clean utility 1 on the same config task and at least 10% lower endpoint
time than the 620-second AW-0019 diagnostic before retaining for broader tests.
Keep all failures and timeout costs. A non-interleaved development result cannot
promote the configuration; the two paired full-suite gates still apply.

## Fixed conditions

Pinned model/runtime/harness, task/verifier, sampler, cache, output cap, timeout,
internal storage, single model owner, and loopback-only endpoint remain unchanged.
The shell working directory remains the true task workspace; `.` denotes it.

## Results and disposition

Pending real harness fixture and endpoint trial. No running experiment loads
this extension. Prepared as an optional next arm, not a default change.
