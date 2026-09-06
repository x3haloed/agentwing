import argparse,json
from .api import list_items
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--limit',type=int,default=10);p.add_argument('--include-archived',action='store_true');a=p.parse_args()
 with open(a.input) as f: records=json.load(f)
 try: result=list_items(records,a.limit,a.include_archived)
 except ValueError as e:p.error(str(e))
 print(json.dumps(result))
if __name__=='__main__':main()
