import pathlib,sys
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w));from cache import Cache
for cap in [0,-1,True,1.5]:
 try:Cache(cap,lambda:0)
 except ValueError:pass
 else:raise AssertionError('capacity')
t=[0];c=Cache(2,lambda:t[0]);c.put('a',None,5);c.put('b',0,10);assert c.get('a','missing') is None;c.put('c',3,10);assert c.get('b','gone')=='gone';t[0]=5;assert c.get('a','gone')=='gone'
c=Cache(2,lambda:t[0]);c.put('live',1,100);c.put('soon',2,1);t[0]=7;c.put('new',3,100);assert c.get('live')==1
c.put('live',4,2);t[0]=8;assert c.get('live')==4;t[0]=9;assert c.get('live') is None
for ttl in [0,-1]:
 try:c.put('x',1,ttl)
 except ValueError:pass
 else:raise AssertionError('ttl')
