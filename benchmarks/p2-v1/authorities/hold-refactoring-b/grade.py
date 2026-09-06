import pathlib,sys
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));import paths,upload,download
for text,out in [('a//./b','a/b'),('./équipe/a b','équipe/a b'),('x.../y','x.../y')]:assert paths.canonical(text)==out and upload.location(text)=='incoming/'+out and download.location(text)=='stored/'+out
for text in ['/root','a/../b','..','','./','a'+chr(92)+'b']:
 for f in [paths.canonical,upload.location,download.location]:
  try:f(text)
  except ValueError:pass
  else:raise AssertionError(text)
seen=[]
def trace(f,e,a):
 if e=='call' and f.f_code is paths.canonical.__code__:seen.append(1)
sys.setprofile(trace)
try:upload.location('a');download.location('b')
finally:sys.setprofile(None)
assert len(seen)==2
