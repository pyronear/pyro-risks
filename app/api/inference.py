# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.


__all__ = ["predictor"]


class Mock:
    def predict(self, date):
        _ = date
        return {"01": {"score": 0.5, "explainability": "weather"}, "02": {"score": 0.5, "explainability": "weather"}}


predictor = Mock()
