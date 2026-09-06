def order(dependencies):
 pending={node:set(ds) for node,ds in dependencies.items()}
 for ds in dependencies.values():
  for node in ds:pending.setdefault(node,set())
 result=[]
 while pending:
  ready=sorted(n for n,ds in pending.items() if not ds)
  if not ready:raise ValueError('cycle')
  node=ready[0];result.append(node);del pending[node]
  for ds in pending.values():ds.discard(node)
 return result
