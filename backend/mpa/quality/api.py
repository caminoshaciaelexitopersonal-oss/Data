
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import pandas as pd
from pydantic import BaseModel

from backend.services.data_quality_service import DataQualityService, get_data_quality_service

router = APIRouter(prefix="/mpa/quality", tags=["MPA - Data Quality"])

class QualityReportRequest(BaseModel):
    data: List[Dict[str, Any]]

    model_config = {
        "extra": "forbid"
    }

@router.post("/report", response_model=Dict[str, Any])
def get_quality_report(
    request: QualityReportRequest,
    service: DataQualityService = Depends(get_data_quality_service)
):
    """
    Generates a comprehensive data quality report for the provided dataset.
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="No data provided.")

    try:
        df = pd.DataFrame(request.data)
        report = service.get_quality_report(df)
        return report
    except Exception as e:
        # It's good practice to log the exception here
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the quality report: {e}")
