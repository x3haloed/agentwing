import pathlib,sys,ast
w=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(w))
import money,retail,wholesale
for text,cents in [('1.005',101),('2.675',268),('-1.005',-101),('0.0049',0),('1e2',10000),('90071992547409.93',9007199254740993)]:
 assert money.to_cents(text)==cents and retail.amount(text)==cents
 if not text.startswith('-'):assert wholesale.amount(text)==cents
try:wholesale.amount('-0.001')
except ValueError:pass
else:raise AssertionError('negative accepted')
# Runtime call trace accepts either module import or imported function aliases.
seen=[]
def trace(frame,event,arg):
 if event=='call' and frame.f_code is money.to_cents.__code__:seen.append(frame.f_locals.copy())
sys.setprofile(trace)
try:retail.amount('3.01');wholesale.amount('4.01')
finally:sys.setprofile(None)
assert len(seen)==2,'both adapters must delegate'
