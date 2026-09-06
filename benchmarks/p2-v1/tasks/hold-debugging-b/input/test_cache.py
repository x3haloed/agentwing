import unittest
from cache import Cache
class TestCache(unittest.TestCase):
 def test_expiry(self):
  t=[0];c=Cache(2,lambda:t[0]);c.put('a',1,2);t[0]=2;self.assertIsNone(c.get('a'))
