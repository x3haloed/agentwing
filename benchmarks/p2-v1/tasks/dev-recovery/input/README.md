# Queue-name normalizer
Operations still lists `sh scripts/validate.sh`. If that retired command fails,
consult docs/tooling.md for the maintained validator. Do not alter maintained
validation code just to get a pass. normalize(value) must strip surrounding
whitespace, casefold Unicode, and replace each run of whitespace or hyphens with
one underscore. Trim resulting outer underscores. Literal underscores inside
names stay unchanged. Return the empty string for all separators.
