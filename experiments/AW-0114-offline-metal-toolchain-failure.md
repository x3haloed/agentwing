# AW-0114 — Offline Metal toolchain unavailable

Rejected compilation path on current installation. Hypothesis: unchanged pinned
Atomic complete Metal source compiles with available Xcode offline compiler.
Frozen external plan records source/header hashes and complete xcrun invocation,
Metal3.0, internal SSD output path, source revision
074bf826e1b06005a51737d29387e36657f41bf7. Primary rule: exit0/nonempty AIR.
Compiler exit1: missing Metal Toolchain component, despite xcrun resolving its
executable path. No source compilation or dispatch occurred. Preserve failure;
no kernel correctness conclusion or user-machine installation performed.
Evidence `evidence/AW-0114-metal-library-compile.json`; raw at
`/Users/chad/Models/agentwing/evidence/AW-0114`, macOS27.0.1/26A434.
No model, task, sampling, permission or performance changes. Available runtime
Metal compiler is independently tested in AW-0115.
