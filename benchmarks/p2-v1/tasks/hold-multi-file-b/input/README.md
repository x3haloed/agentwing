# Audit export redaction
redactor.api.clean(value) returns a deep independent copy, replacing any value
under a dict key matching rules.SECRET_KEYS case-insensitively with "[REDACTED]".
Recurse through dictionaries and lists. Preserve non-secret scalars, empty
containers and key spelling. CLI: python3 -m redactor.cli INPUT.jsonl OUTPUT.jsonl.
Process one JSON value per nonblank line; preserve row order. Parse the whole
input before overwriting output, so malformed JSON leaves prior output intact.
Do not change rules.py or source input. Unicode and nested arrays are supported.
