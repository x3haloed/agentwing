from collections import OrderedDict
class Cache:
 def __init__(self,capacity,clock):
  if type(capacity) is not int or capacity<=0:raise ValueError('capacity')
  self.capacity=capacity;self.clock=clock;self.data=OrderedDict()
 def put(self,key,value,ttl):
  if ttl<=0:raise ValueError('ttl')
  now=self.clock()
  for k,(_,expiry) in list(self.data.items()):
   if expiry<=now:del self.data[k]
  self.data[key]=(value,now+ttl);self.data.move_to_end(key)
  while len(self.data)>self.capacity:self.data.popitem(last=False)
 def get(self,key,default=None):
  if key not in self.data:return default
  value,expiry=self.data[key]
  if self.clock()>=expiry:del self.data[key];return default
  self.data.move_to_end(key);return value
