# Window merger
`windows.merge` takes an iterable of integer half-open intervals [start, end).
Return a sorted list of disjoint tuples. Merge overlapping or touching windows.
Drop empty windows, reject reversed windows with ValueError, and never mutate
caller input. Iterators are supported. Run `python3 -m unittest -q`.
