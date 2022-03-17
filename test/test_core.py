# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import unittest

import pyro_risks


class CoreTester(unittest.TestCase):
    # Template unittest
    def test_version(self):
        self.assertEqual(len(pyro_risks.__version__.split(".")), 3)


if __name__ == "__main__":
    unittest.main()
