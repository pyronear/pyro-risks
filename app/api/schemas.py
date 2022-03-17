# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import Optional
from pydantic import BaseModel, Field


class RegionRisk(BaseModel):
    geocode: str = Field(..., example="01")
    score: float = Field(..., gt=0, lt=1, example=0.5)
    explainability: Optional[str] = Field(None, example="weather")
