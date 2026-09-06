def project(events):
 balances={};seen=set()
 for e in events:
  identity=(e['tenant'],e['event_id'])
  if identity in seen:continue
  seen.add(identity);key=e['tenant']+'/'+e['account'];balances[key]=balances.get(key,0)+e['delta']
 return dict(sorted(balances.items()))
