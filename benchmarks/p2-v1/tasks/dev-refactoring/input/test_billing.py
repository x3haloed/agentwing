import unittest,retail,wholesale
class Billing(unittest.TestCase):
 def test_tie(self):self.assertEqual(retail.amount('1.005'),101)
 def test_wholesale(self):self.assertEqual(wholesale.amount('2.50'),250)
