import unittest
from ledger.api import list_items
class TestLedger(unittest.TestCase):
 def test_filter_before_limit(self):self.assertEqual(list_items([{'id':1,'archived':True},{'id':2}],1),[{'id':2}])
