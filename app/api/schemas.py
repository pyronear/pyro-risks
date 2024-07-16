# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import Optional
from pydantic import BaseModel, Field


class RegionRisk(BaseModel):
    geocode: str = Field(..., examples=["01"])
    score: float = Field(..., gt=0, lt=1, examples=[0.5])
    explainability: Optional[str] = Field(None, examples=["weather"])


class ScoreQueryParams(BaseModel):
    longitude: float = Field(..., gt=-90.0, lt=90.0)
    latitude: float = Field(..., gt=-180.0, lt=180.0)
    crs: str = Field(
        default="EPSG:2154",
        examples=["EPSG:2154"],
        description="Coordinate Reference System  (CRS), Default to France reference CRS (RGF93 / Lambert 93).",
    )


class Score(BaseModel):
    longitude: float = Field(..., gt=-90.0, lt=90.0, examples=[])
    latitude: float = Field(..., gt=-180.0, lt=180.0, examples=[])
    crs: str = Field(..., examples=["EPSG:4326"], description="")
    score: str = Field(..., examples=[], description="FWI")
    value: float = Field(..., examples=[], description="")
