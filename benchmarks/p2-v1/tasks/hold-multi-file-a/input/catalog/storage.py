import json
def save(path,records):
 with open(path,'w') as f:json.dump(records,f)
