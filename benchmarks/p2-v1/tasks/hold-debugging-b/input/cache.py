class Cache:
 def __init__(self,capacity,clock):self.capacity=capacity;self.clock=clock;self.data={}
 def put(self,key,value,ttl):
  self.data[key]=(value,self.clock()+ttl)
  if len(self.data)>self.capacity:del self.data[next(iter(self.data))]
 def get(self,key,default=None):
  entry=self.data.get(key)
  return entry[0] if entry else default
