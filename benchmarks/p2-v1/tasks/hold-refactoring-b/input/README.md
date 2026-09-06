# Artifact locations
Create paths.canonical(text) and make upload.location(text) and download.location(text)
call it. Return respectively "incoming/" and "stored/" plus its result.
Canonicalization: reject absolute paths, backslashes, and any .. segment with
ValueError. Drop empty and . segments, join remaining segments with /, reject
empty result. Preserve spaces and Unicode in remaining segments. No filesystem
access. Public callers and shared function must agree on errors.
