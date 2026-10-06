# AW-0195: Actual failed trajectory versus historical isolated request

Status: offline reconstruction complete; retained diagnostic evidence.

Reconstruct AW-0194's seven completed Pi messages before its nonterminal
fourth request through the installed native OpenAI adapter. Include the
installed custom-prompt builder's appended working-directory line. Borrow
AW-0145's retained native tool schema; this is reconstruction, not capture
of AW-0194 HTTP wire bytes. No model runs or tools execute.

Normalize only random call identifiers, preserving associations. Historical
AW-0145 and current AW-0194 system prompt and user task match, but all three
assistant reasoning strings, commands and tool results differ. Nine changed
fields remain. Consequently AW-0193 success and AW-0194 timeout are not an
identical-request causal comparison; do not attribute the discrepancy to
cache reuse, checkpoint restoration or numeric state alone.

Receipt: `evidence/AW-0195-stationary-request-comparison.json` pins inputs,
adapter, prompt builder, script, raw reconstructions and changed-field hashes.
Large/raw task contents stay external in
`/Users/chad/Models/agentwing/evidence/AW-0195`. Initial reconstruction
incorrectly omitted the cwd suffix; preserve its artifacts and hashes under
`attempt-0-missing-cwd-suffix`, rather than treating that apparent prompt
change as evidence of harness drift.

Reproduce: use the pinned Node binary with
`scripts/compare_bonsai_stationary_requests.mjs`.
Next use the current reconstructed request for a same-history cache screen
before another endpoint attempt. All original task, reasoning, permission,
timeout and scoring gates remain fixed. P1 unchanged; no promotion claim.
