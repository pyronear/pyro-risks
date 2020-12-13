from typing import List
from fastapi import APIRouter
from app.api.inference import predictor
from app.api.schemas import RegionRisk


router = APIRouter()


@router.get("/{country}/{date}", response_model=List[RegionRisk], summary="Computes the wildfire risk for the given country")
async def get_pyrorisk(country: str, date: str):
    """Using the country identifier, this will compute the wildfire risk for all known subregions"""
    preds = predictor.predict(date)
    return [RegionRisk(geocode=k, score=v['score'], explainability=v['explainability']) for k, v in preds.items()]
