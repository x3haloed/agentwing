# Build planner
order(dependencies) returns each named node once, after all its dependencies.
Nodes include both mapping keys and dependency-only names. At every step choose
the lexicographically smallest currently ready name (not whole-level sorting).
Cycles, including self-cycles, raise ValueError. Duplicate dependency entries
count once. Input lists must be unchanged. Empty mapping returns [].
