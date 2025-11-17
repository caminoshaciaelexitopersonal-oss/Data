
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
import pandas as pd

from backend.services.anomaly_service import AnomalyService, get_anomaly_service
from pydantic import BaseModel

class AnomalyRequest(BaseModel):
    data: List[Dict[str, Any]]
    columns: List[str]
    contamination: float = 0.1

router = APIRouter(prefix="/mpa/ml", tags=["MPA - Machine Learning"])

@router.post("/anomaly-detection", response_model=Dict[str, Any])
def run_anomaly_detection(
    request: AnomalyRequest = Body(...),
    service: AnomalyService = Depends(get_anomaly_service)
):
    """
    Runs anomaly detection on the provided dataset using IsolationForest.
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="No data provided.")
    if not request.columns:
        raise HTTPException(status_code=400, detail="No columns specified for anomaly detection.")

    try:
        df = pd.DataFrame(request.data)
        result = service.detect_anomalies(df, request.columns, request.contamination)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during anomaly detection: {e}")
