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
        default="EPSG:4326",
        examples=["EPSG:4326"],
        description="Coordinate Reference System (CRS), Default to World Geodetic System CRS (EPSG:4326 / WGS84).",
    )


class Score(BaseModel):
    longitude: float = Field(..., gt=-90.0, lt=90.0, examples=[2.638828])
    latitude: float = Field(..., gt=-180.0, lt=180.0, examples=[48.391842])
    crs: str = Field(..., examples=["EPSG:4326"], description="Coordinate Reference System (CRS).")
    score: str = Field(..., examples=["fwi"], description="Score name.")
    value: float = Field(..., examples=[2, 1], description="Score value.")
    date: str = Field(..., examples=["2024-01-01"], description="Date in %Y-%m-%d format")
