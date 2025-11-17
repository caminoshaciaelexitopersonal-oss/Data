
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
import pandas as pd

from backend.services.eda_intelligent_service import EdaIntelligentService, get_eda_intelligent_service

router = APIRouter(prefix="/mpa/eda", tags=["MPA - EDA"])

@router.post("/intelligent", response_model=Dict[str, Any])
def run_intelligent_eda(
    data: List[Dict[str, Any]] = Body(...),
    service: EdaIntelligentService = Depends(get_eda_intelligent_service)
):
    """
    Runs a full suite of intelligent EDA tools on the provided dataset.
    """
    if not data:
        raise HTTPException(status_code=400, detail="No data provided.")

    try:
        df = pd.DataFrame(data)

        # Execute all intelligent EDA functions
        summary = service.auto_summary(df)
        distributions = service.auto_detect_distributions(df)
        outliers = service.auto_detect_outliers(df)
        visualizations = service.auto_visualizations(df)

        return {
            "summary": summary,
            "distributions": distributions,
            "outliers": outliers,
            "visualizations": visualizations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during EDA: {e}")
