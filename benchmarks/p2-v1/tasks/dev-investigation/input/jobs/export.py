import json,sys
from .join import enrich
def export(invoices,customers):
 totals={}
 for row in enrich(invoices,customers):totals[row['tenant_id']]=totals.get(row['tenant_id'],0)+row['cents']
 return dict(sorted(totals.items()))
if __name__=='__main__':
 with open(sys.argv[1]) as f: invoices=json.load(f)
 with open(sys.argv[2]) as f: customers=json.load(f)
 with open(sys.argv[3],'w') as f:json.dump(export(invoices,customers),f)
