import unittest

import pyro_risks


class CoreTester(unittest.TestCase):
    # Template unittest
    def test_version(self):
        self.assertEqual(len(pyro_risks.__version__.split(".")), 3)


if __name__ == "__main__":
    unittest.main()
