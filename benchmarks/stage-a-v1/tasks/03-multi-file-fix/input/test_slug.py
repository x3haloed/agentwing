import unittest

from slug import display_slug


class SlugTests(unittest.TestCase):
    def test_spaces_and_empty_words(self):
        self.assertEqual(display_slug("Fast  Local Agent"), "docs/fast-local-agent")


if __name__ == "__main__":
    unittest.main()
