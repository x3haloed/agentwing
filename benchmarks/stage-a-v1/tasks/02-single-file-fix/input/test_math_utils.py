import unittest

from math_utils import clamp


class ClampTests(unittest.TestCase):
    def test_inside(self):
        self.assertEqual(clamp(4, 0, 10), 4)

    def test_edges(self):
        self.assertEqual(clamp(-2, 0, 10), 0)
        self.assertEqual(clamp(22, 0, 10), 10)


if __name__ == "__main__":
    unittest.main()
