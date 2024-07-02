# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.


__all__ = ["predictor"]


class Mock:
    def predict(self, date):
        return {"01": 0.5, "02": 0.5}


predictor = Mock()
