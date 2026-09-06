# INI migration
CLI python3 convert.py IN.ini OUT.json. Function convert(text) parses interpolation-
free INI. [server] port defaults to 8080, positive integer <=65535; enabled defaults
to true, accepting case-insensitive true/false, yes/no, 1/0 only. timeout_ms defaults
1500, nonnegative integer. Output {"server":{"port":int,"enabled":bool,
"timeout_seconds":float,...unknown server string settings},"extras":{...other
sections as string-valued mappings}}. Preserve percent signs in values. Reject
invalid typed settings with ValueError. Do not modify the source file.
