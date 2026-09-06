from urllib.parse import quote
def url(params):
 parts=[]
 for k in sorted(params):
  for v in params[k] if isinstance(params[k],list) else [params[k]]:parts.append(quote(str(k),safe='')+'='+quote(str(v),safe=''))
 return '/report?'+'&'.join(parts)
