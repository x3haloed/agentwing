import importlib.util, pathlib, sys, random
w=pathlib.Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('submitted_windows',w/'windows.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for source,expected in [([],[]),([(0,0)],[]),([(1,9),(3,5)],[(1,9)]),([(3,4),(1,3)],[(1,4)]),([(-5,-2),(-2,0),(4,6)],[(-5,0),(4,6)])]:
 before=list(source);assert m.merge(source)==expected;assert source==before;assert m.merge(iter(source))==expected
try:m.merge([(4,2)])
except ValueError:pass
else:raise AssertionError('reversed interval accepted')
# Independent integer-coverage oracle, not the submitted merge algorithm.
rng=random.Random(8021)
for _ in range(100):
 source=[tuple(sorted([rng.randrange(-15,16),rng.randrange(-15,16)])) for _ in range(12)]
 covered={x for a,b in source for x in range(a,b)};actual=m.merge(iter(source))
 assert all(a<b for a,b in actual)
 assert all(actual[i][1]<actual[i+1][0] for i in range(len(actual)-1))
 assert {x for a,b in actual for x in range(a,b)}==covered
