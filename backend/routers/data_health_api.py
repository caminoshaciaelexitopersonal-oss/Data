from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Dict, Any
import pandas as pd

from backend.mpa.eda.service import EdaService, eda_service

router = APIRouter(tags=["Data Health"])

def get_eda_service():
    # Dependency injection for the EDA service
    return eda_service

@router.post("/data-health-report")
async def get_data_health_report(
    data: List[Dict[str, Any]] = Body(..., embed=True),
    service: EdaService = Depends(get_eda_service)
):
    """
    Receives a dataset and returns a data health report.
    """
    if not data:
        raise HTTPException(status_code=400, detail="No data provided.")

    try:
        df = pd.DataFrame(data)
        report = service.generate_data_health_report(df)
        if report.get("status") == "error":
            raise HTTPException(status_code=500, detail=report.get("message"))
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the data health report: {e}")
