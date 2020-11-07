import unittest
import pyronear_ds


class CoreTester(unittest.TestCase):
    # Template unittest
    def test_version(self):
        self.assertEqual(len(pyronear_ds.__version__.split(".")), 3)


if __name__ == "__main__":
    unittest.main()
