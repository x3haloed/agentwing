import json
import unittest


class ConfigTests(unittest.TestCase):
    def test_policy(self):
        with open("config.json", encoding="utf-8") as handle:
            config = json.load(handle)
        self.assertEqual(config["bind"], "127.0.0.1")
        self.assertEqual(config["max_tool_result_chars"], 4096)
        self.assertEqual(config["experiment"], "stage-a")


if __name__ == "__main__":
    unittest.main()
