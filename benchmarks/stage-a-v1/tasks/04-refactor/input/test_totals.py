import unittest

from alpha import alpha_total
from beta import beta_total


class TotalTests(unittest.TestCase):
    def test_public_functions(self):
        self.assertEqual(alpha_total([-2, 1, 3]), 4)
        self.assertEqual(beta_total([5, -1, 2]), 7)

    def test_shared_implementation(self):
        import totals
        self.assertEqual(totals.nonnegative_total([-1, 2]), 2)


if __name__ == "__main__":
    unittest.main()
