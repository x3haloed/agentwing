def project(events):
 balances={}
 for e in events:
  key=e['tenant']+'/'+e['account'];balances[key]=balances.get(key,0)+e['delta']
 return dict(sorted(balances.items()))
