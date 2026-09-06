# Schema migration
upgrade(config) returns a new dict, leaving nested input structures untouched.
Schema 1: replace timeout_seconds with network.timeout_ms (multiply by 1000),
and retries with network.attempts (retries+1). These source fields default to
30 and 2; they are nonnegative integers, excluding booleans. Merge into any
existing network dict, overwriting migrated timeout_ms/attempts only. Preserve
all unrelated top-level and nested keys. Remove only timeout_seconds and retries;
set schema=2. Schema 2 returns an equal independent deep copy. Reject other schema
versions and invalid schema-1 values with ValueError. CLI: python3 migrate.py IN OUT.
