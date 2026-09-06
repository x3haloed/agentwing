import pathlib,sys,copy,itertools,random
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from planner import order
for inp,expected in [({},[]),({'a':['z']},['z','a']),({'a':['b'],'b':[],'z':[]},['b','a','z']),({'c':['a','a'],'a':[]},['a','c'])]:
 before=copy.deepcopy(inp);assert order(inp)==expected;assert inp==before
for inp in [{'a':['a']},{'a':['b'],'b':['a']},{'x':[],'a':['b'],'b':['a']}]:
 try:order(inp)
 except ValueError:pass
 else:raise AssertionError('cycle accepted')
# Exhaustive permutation oracle on small acyclic graphs.
rng=random.Random(782)
for _ in range(20):
 nodes=['a','b','c','d'];rng.shuffle(nodes);g={n:[p for p in nodes[:i] if rng.randrange(2)] for i,n in enumerate(nodes)}
 valid=[p for p in itertools.permutations(sorted(nodes)) if all(p.index(d)<p.index(n) for n,ds in g.items() for d in ds)]
 assert order(g)==list(min(valid))
