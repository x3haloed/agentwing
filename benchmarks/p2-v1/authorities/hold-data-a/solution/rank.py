import csv,json,sys
teams={}
with open(sys.argv[1],newline='') as f:
 for r in csv.DictReader(f,delimiter='	'):
  players=teams.setdefault(r['team'],{});name=r['player'];score=int(r['score']);players[name]=max(players.get(name,score),score)
out={}
for team in sorted(teams):
 rows=[];previous=None;rank=0
 for i,(player,score) in enumerate(sorted(teams[team].items(),key=lambda x:(-x[1],x[0])),1):
  if score!=previous:rank=i
  rows.append(dict(player=player,score=score,rank=rank));previous=score
 out[team]=rows
with open(sys.argv[2],'w') as f:json.dump(out,f)
