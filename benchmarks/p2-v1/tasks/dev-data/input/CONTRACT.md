# Revisioned event aggregation
CLI: python3 summarize.py INPUT.csv OUTPUT.json
Columns: event_id,revision,service,cents,deleted. CSV quoting is standard.
For each event_id retain its highest integer revision, regardless of input order.
Repeated rows at the same revision are identical. deleted=1 removes that event
from aggregation; deleted=0 keeps it. Sum signed integer cents by service, preserve
service spelling, and sort service names. Output JSON: {"events": N,"cents_by_service":{...}}.
Empty input with headers gives zero events and an empty mapping. Do not modify
input. Existing outputs must be replaced, not appended. Use standard Python only.
