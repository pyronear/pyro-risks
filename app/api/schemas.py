from typing import Optional
from pydantic import BaseModel, Field


class RegionRisk(BaseModel):
    geocode: str = Field(..., example="01")
    score: float = Field(..., gt=0, lt=1, example=0.5)
    explainability: Optional[str] = Field(None, example="weather")
