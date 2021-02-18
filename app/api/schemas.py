# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from typing import Optional
from pydantic import BaseModel, Field


class RegionRisk(BaseModel):
    geocode: str = Field(..., example="01")
    score: float = Field(..., gt=0, lt=1, example=0.5)
    explainability: Optional[str] = Field(None, example="weather")
