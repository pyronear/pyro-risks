# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import Dict, Any
from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from app.api.schemas import ScoreQueryParams, Score
from pyrorisks.platform_fwi.get_fwi_effis_score import get_fwi as _get_fwi


router = APIRouter()


@router.get(path="/", response_model=Score, summary="Provide European Forest Fire Information System (EFFIS) Fire Weather Index (FWI) categories.")
async def get_fwi(query: ScoreQueryParams = Depends()) -> Dict[str, Any]:
   results = _get_fwi(longitude=query.longitude, latitude=query.latitude, crs=query.crs)
   if results is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fire Weather Index (FWI) for longitude {query.longitude} and latitude {query.latitude} was not found."
        )
   return results