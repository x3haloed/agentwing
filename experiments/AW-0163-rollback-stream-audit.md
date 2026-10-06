# AW-0163 — full-request wire audit negative fixtures

Audit instrumentation verification, not a new model performance experiment.
Rules derive from RED_LINES protocol-corruption gate. Fixtures and changes were
written before execution; this is a retrospective verification record, not
claimed preregistration. AW162 runner/request/runtime/model/profile unchanged.

Independent stream audit now rejects duplicateDONE, data afterDONE, tool ID
changes, duplicate JSON keys, invalid JSON constants and nonfinite timeouts.
Incomplete arguments stay incomplete rather than completed-malformed attempts.
Six synthetic public fixture test groups pass, including valid fragmented bash,
missing terminal, malformed arguments and completion-ID corruption. No tools
execute. Command: python3 -m unittest discover -s tests -p test_rollback_stream_audit.py.

Both historical AW149 raw streams replay: FP16 retains valid terminal proposal;
Turbo remains incomplete. Preserve all old receipts and scores. No endpoint
verifier/task/timeout/tool/reasoning change or quality/speed claim. AW162 live
stream currently has no detected wire corruption, but is nonterminal.

External test log /Users/chad/Models/agentwing/evidence/AW-0163;
source/OS/Python/test/historical-stream hashes in
evidence/AW-0163-rollback-stream-audit.json. Retain protocol audit; no promotion.
