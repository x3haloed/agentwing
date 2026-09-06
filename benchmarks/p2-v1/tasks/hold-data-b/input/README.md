# Session duration export
CLI: python3 durations.py IN.json OUT.json. Input is a JSON list of events with
session,kind (start or stop), at (ISO timestamp with offset or Z), and service.
For each session use earliest start and latest stop, regardless of input order.
Ignore sessions missing either kind; service comes from the earliest start.
Sum elapsed integer seconds per service in UTC. Reject negative durations with
ValueError from totals(events). Preserve inputs and sort output service keys.
