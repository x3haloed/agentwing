import json,sys
from .storage import save
def main():
 with open(sys.argv[1]) as f:records=json.load(f)
 save(sys.argv[2],records)
if __name__=='__main__':main()
