# HTTP clients
Move query encoding into query.encode(params). Both search.url(params) and
report.url(params) must call it and retain their /search? and /report? prefixes.
Sort parameter keys. For list values emit repeated keys in list order. Empty lists
emit nothing. Convert scalar values with str, including None. Percent-encode
UTF-8 with spaces as %20 (never +), preserving only RFC unreserved characters.
Keep blank strings as key=. Do not mutate caller dictionaries or lists.
