import csv,json,sys
with open(sys.argv[1]) as f:rows=list(csv.DictReader(f))
result={}
for r in rows:result[r['service']]=result.get(r['service'],0)+int(r['cents'])
with open(sys.argv[2],'w') as f:json.dump({'events':len(rows),'cents_by_service':result},f)
