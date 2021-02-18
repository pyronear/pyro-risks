# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

import unittest

import pyro_risks


class CoreTester(unittest.TestCase):
    # Template unittest
    def test_version(self):
        self.assertEqual(len(pyro_risks.__version__.split(".")), 3)


if __name__ == "__main__":
    unittest.main()
