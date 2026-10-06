# AW-0111 — Metal WHT harness failure

Rejected harness. Hypothesis: unchanged Atomic forward/inverse Metal WHT agrees
with CPU within predeclared relative L2 .005 on AW-0109 complete real populated
Q/V row collections at layers3/31/63. Compilation and extraction succeeded,
but CPU symbol lookup failed before first Metal dispatch: forward function is
static, only inverse is exported. Exit1 is preserved, not a kernel failure.
Frozen plan/source/compiled binary/input/failure hashes live in
`evidence/AW-0111-metal-wht.json`; raw evidence at
`/Users/chad/Models/agentwing/evidence/AW-0111` on internal SSD.
No model owner, task/tool/sampling changes, quality or speed claim. Host preflight
passed on fixed M1/16GB/macOS27.0.1. AW-0112 separately freezes inverse-only
coverage needed for q8-K/Turbo-V asymmetric path; AW-0111 is not rewritten.
