import csv,json,sys
latest={}
with open(sys.argv[1],newline='') as f:
 for row in csv.DictReader(f):
  if row['event_id'] not in latest or int(row['revision'])>int(latest[row['event_id']]['revision']):latest[row['event_id']]=row
counts={};n=0
for row in latest.values():
 if row['deleted']=='1':continue
 n+=1;service=row['service'];counts[service]=counts.get(service,0)+int(row['cents'])
with open(sys.argv[2],'w') as f:json.dump({'events':n,'cents_by_service':dict(sorted(counts.items()))},f)
