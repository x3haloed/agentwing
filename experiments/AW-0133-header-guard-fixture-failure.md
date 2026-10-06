# AW-0133 — Header-guard fixture prerequisite failure

Rejected fixture. Review found inverse argument struct appended outside existing
Metal header guard. Freeze before/after header texts and compare repeated-include
syntax compilation before changing source. Initial standalone fixture includes
integer definitions but omits size_t prerequisite; both variants fail before
validating the hypothesis. No source mutation occurred because assertion stopped
execution. No model/runtime/host-performance result. Preserve raw prerequisite
errors under `/Users/chad/Models/agentwing/evidence/AW-0133`; metadata
`evidence/AW-0133-prism-inverse.json`. Correct prerequisite under separate AW-0134.
