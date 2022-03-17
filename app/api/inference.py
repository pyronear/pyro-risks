# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from pyro_risks.models.predict import PyroRisk


__all__ = ["predictor"]


predictor = PyroRisk(which="RF")
