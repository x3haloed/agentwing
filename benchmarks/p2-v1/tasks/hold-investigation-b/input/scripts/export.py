import pathlib,sys,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from release.summarize import summarize
with open(sys.argv[1]) as f:builds=json.load(f)
with open(sys.argv[2],'w') as f:json.dump(summarize(builds),f)
