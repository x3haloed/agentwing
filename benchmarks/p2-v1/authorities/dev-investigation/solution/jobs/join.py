def enrich(invoices,customers):
 index={(c['tenant_id'],c['customer_id']):c for c in customers}
 result=[]
 for invoice in invoices:
  key=(invoice['tenant_id'],invoice['customer_id'])
  if key not in index:raise ValueError('unknown customer')
  result.append(dict(invoice,name=index[key]['name']))
 return result
