# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from pyro_risks.datasets.utils import download
import pyro_risks.config as cfg

if __name__ == "__main__":
    download(
        url=cfg.ERA5T_VIIRS_PIPELINE,
        default_extension="csv",
        unzip=False,
        destination=cfg.DATA_REGISTRY,
    )
