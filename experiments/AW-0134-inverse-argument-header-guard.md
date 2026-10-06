# AW-0134 — Guard inverse argument declaration

Retained source fix. Predeclare repeated-header syntax check with required
stdint/size_t prerequisites: old header must fail repeated typedef; identical
argument declaration moved inside existing guard must compile, sizeof16.
Both variants hashed before compile. clang++ C++17 fsyntax-only old exit1 due
redefinition, corrected exit0. Argument fields/types unchanged; no arithmetic
or ABI layout change. Only after successful checks, move actual experimental
source declaration into guard. No runtime binaries overwritten or rebuilt.

Frozen full updated patch `experiments/runtime-patches/AW-0134-turbo-inverse-guarded.patch`
applies cleanly to exact Prism baseline. Source port now carries corrected
placement; AW-0131/AW-0132 binaries/results preserved with their original hashes.
New source revision requires build before model launch/claims. No inference,
sampling/task/tool/permission or host-performance claim. Evidence
`evidence/AW-0134-prism-inverse.json`; raw before/after headers/fixtures/compiler
logs and patch `/Users/chad/Models/agentwing/evidence/AW-0134`. Prior malformed
standalone fixture failure AW-0133 preserved. P1/current launcher intact.
