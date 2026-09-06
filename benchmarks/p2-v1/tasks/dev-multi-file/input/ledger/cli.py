import argparse,json
from .api import list_items
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--limit',type=int,default=10);a=p.parse_args()
 with open(a.input) as f: records=json.load(f)
 print(json.dumps(list_items(records,a.limit)))
if __name__=='__main__':main()
