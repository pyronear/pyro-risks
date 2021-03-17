# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from pyro_risks.load import load_dataset
from unittest import mock

import pyro_risks.config as cfg
import unittest
import tempfile
import os


class LoadTester(unittest.TestCase):
    def test_load(self):
        with tempfile.TemporaryDirectory() as destination:
            with mock.patch("pyro_risks.config.DATA_REGISTRY", destination):
                dataset_path = os.path.join(destination, cfg.DATASET)
                load_dataset()
                self.assertTrue(os.path.isfile(dataset_path))


if __name__ == "__main__":
    unittest.main()
