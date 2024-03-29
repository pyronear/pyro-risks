# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from pyro_risks.pipeline import load_dataset
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
