import unittest
from windows import merge
class TestWindows(unittest.TestCase):
 def test_contained(self):self.assertEqual(merge([(1,9),(3,5)]),[(1,9)])
 def test_touching(self):self.assertEqual(merge([(1,3),(3,4)]),[(1,4)])
