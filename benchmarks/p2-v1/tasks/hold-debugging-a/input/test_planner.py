import unittest
from planner import order
class Planner(unittest.TestCase):
 def test_dependency(self):self.assertEqual(order({'a':['z']}),['z','a'])
