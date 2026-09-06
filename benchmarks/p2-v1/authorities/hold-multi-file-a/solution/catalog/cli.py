import argparse,json
from .storage import save
def main():
 p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');p.add_argument('--sort-by-id',action='store_true');a=p.parse_args()
 with open(a.input) as f:records=json.load(f)
 if a.sort_by_id:records=sorted(records,key=lambda r:r['id'])
 save(a.output,records)
if __name__=='__main__':main()
