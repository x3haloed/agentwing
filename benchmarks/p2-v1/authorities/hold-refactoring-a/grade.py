import pathlib,sys,copy
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));import query,search,report
for params,encoded in [({},''),({'z':['a b','c/d'],'a':''},'a=&z=a%20b&z=c%2Fd'),({'é':'雪','n':None,'empty':[]},'n=None&%C3%A9=%E9%9B%AA'),({'x':'a+b&c=~'},'x=a%2Bb%26c%3D~')]:
 before=copy.deepcopy(params);assert query.encode(params)==encoded;assert search.url(params)=='/search?'+encoded;assert report.url(params)=='/report?'+encoded;assert params==before
seen=[]
def trace(f,e,a):
 if e=='call' and f.f_code is query.encode.__code__:seen.append(1)
sys.setprofile(trace)
try:search.url({});report.url({})
finally:sys.setprofile(None)
assert len(seen)==2
