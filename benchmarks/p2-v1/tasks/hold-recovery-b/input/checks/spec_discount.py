import unittest
from discount import apply
class Discount(unittest.TestCase):
 def test_half(self):self.assertEqual(apply(101,50),51)
 def test_invalid(self):
  with self.assertRaises(ValueError):apply(1,101)
