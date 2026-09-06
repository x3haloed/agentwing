# Feature flags v1 to v2
CLI: python3 upgrade.py IN OUT. Function upgrade(config) returns a deep copy.
v1 has flags as a list of {name,enabled,...metadata}. Convert to a dict keyed by
name, with each value containing enabled and the remaining metadata. Reject
repeated names, empty/non-string names, or non-boolean enabled with ValueError.
Missing flags means empty list. Preserve unrelated top-level fields; version
becomes 2. v2 inputs are returned as equal independent deep copies. Reject unknown
versions. Never modify the original config or nested metadata.
