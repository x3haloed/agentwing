# AW-0075 — Malformed tool evidence rejects without crashing the scorer

Retained no-model falsifiers, 2026-10-05.

AW72 malformed empty bash arguments are correctly blocked by Pi, but scorer
command extraction raises KeyError and loses its task row. Do not repair or
rescore the frozen run into success. New AW76 checker uses type-safe extraction,
counts valid/malformed calls individually and retains command null when absent.
Its schema failure still aborts qualification; it does not infer missing commands,
execute them, relax protocol or permit history loss.

Actual malformed refactor trace, null args and integer command are all rejected
without exception: attempted6,valid5,malformed1. A valid original navigation trace
returns exactly the previous protocol dictionary. Evidence/source hash:
`evidence/AW-0075-malformed-command-falsifiers.json`. Temporary mutations only;
original raw traces and frozen corpus unchanged. This fixes evidence collection,
not model capability or rate. AW74 remains unexecuted; AW76 has a fresh plan.
