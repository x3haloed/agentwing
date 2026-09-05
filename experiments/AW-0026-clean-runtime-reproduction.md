# AW-0026 — Clean runtime reproduction

## Status

Frozen for clean checkout, build, and test validation.

## Hypothesis and acceptance

The pinned Swiftlet source can be built and tested from an independent clean
checkout with the resolved dependency versions, without relying on the existing
build directory. Require the recorded source tree, clean tracked files after
build, passing complete Swift tests, and a release server binary. Source
reconstruction from the archived upstream patch series has already matched this
tree; this experiment adds clean build/test evidence, not a speed claim.

## Fixed identity

Runtime commit `459b2011375022a6716463bd1e1f1b00741f91c3`, source tree
`2f1cbc79a36fe3a46c7bc43701ff4e77f2c5ec6c`. Clone the local source repository
without hardlinks into a new Agentwing-owned reproduction directory, detach
at the pinned commit, and verify the tree. Existing model payloads, sources,
results, and the working runtime build are preserved. Use two build jobs;
no model process runs concurrently. Record compiler/OS/architecture and logs.

## Commands

Build release with `swift build -c release --jobs 2 --disable-automatic-resolution`.
Run `swift test --jobs 2 --disable-automatic-resolution`. Record test counts,
exit codes, dependency lock hash, source tree, and executable hashes. Differences
in compiled bytes alone can reflect checkout paths; do not claim bit-identical
binaries or endpoint equivalence without checking. A new real-model or paired
run must still record which actual binary it uses.

## Results and disposition

Passed: independent release build and all 180 tests in 29 suites. Tracked
checkout remains clean. See `evidence/AW-0026-clean-build.json` for log hashes.
The executable hash differs from the original build; this proves source/build
reproduction, not byte-identical compilation or endpoint equivalence. Paired
runs will use the original pinned executable in both arms. Retained.
