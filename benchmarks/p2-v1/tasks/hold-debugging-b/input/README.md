# Expiring LRU
Cache(capacity, clock) uses the injected callable clock, returning seconds.
put(key,value,ttl) stores a value until clock()+ttl. ttl must be positive, or
ValueError. A key is expired at time >= expiry. get(key,default=None) returns
default for missing/expired entries and makes live entries most recently used.
put of an existing key refreshes value, expiry and recency. Remove expired entries
before evicting the least recently used live entry when capacity is exceeded.
Capacity is a positive integer excluding bool. Values may be None or falsey.
