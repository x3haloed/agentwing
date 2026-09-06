def enrich(invoices,customers):
 result=[]
 for invoice in invoices:
  for customer in customers:
   if invoice['customer_id']==customer['customer_id']:
    result.append(dict(invoice,tenant_id=customer['tenant_id'],name=customer['name']))
 return result
