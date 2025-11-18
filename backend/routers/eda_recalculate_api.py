from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
import pandas as pd

from backend.mpa.eda.service import EdaService, eda_service

router = APIRouter(prefix="/mpa/eda", tags=["MPA - EDA"])

def get_eda_service():
    # Dependency injection for the EDA service
    return eda_service

@router.post("/recalculate")
async def recalculate_eda(
    data: List[Dict[str, Any]] = Body(..., embed=True),
    service: EdaService = Depends(get_eda_service)
):
    """
    Receives a dataset and returns a new set of EDA visualizations.
    """
    if not data:
        raise HTTPException(status_code=400, detail="No data provided.")

    try:
        df = pd.DataFrame(data)
        visualizations = service.generate_eda_plots(df)
        return visualizations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during EDA recalculation: {e}")
