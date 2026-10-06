# AW-0067 — Reject history-loss events in candidate diagnostics

Retained no-model checker evidence, 2026-10-05. No model experiment launched.

Saved AW64 navigation traces are copied to temporary directories. A static
"context shift is disabled" line must pass; an actual shift with n_discard128
must fail; a compaction_start event must fail. Baseline tool/request pairing,
cleanup and original traces are preserved. All three decisions match expected.
Initial result: `evidence/AW-0067-history-checks.json`. Revalidation against the
frozen supported-thinking AW72 runner: `evidence/AW-0067-history-revalidation.json`,
including exact checker and fixture hashes. Temporary copies are removed after
checking; original raw evidence and corpus remain unchanged. The earlier
unlaunched temperature-zero development proposal was superseded before freezing
or model execution. No held-out task exposed and no capability claim follows.
