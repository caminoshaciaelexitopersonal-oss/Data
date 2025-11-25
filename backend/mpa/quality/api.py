from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any
from pydantic import BaseModel

from backend.mpa.quality.service import DataQualityService, get_data_quality_service
from backend.app.services.state_store import StateStore, get_state_store

router = APIRouter(tags=["MPA - Data Quality"])

class SessionRequest(BaseModel):
    """Defines the standard request model for session-based operations."""
    session_id: str

@router.post("/report", response_model=Dict[str, Any])
def get_quality_report(
    request: SessionRequest = Body(...),
    service: DataQualityService = Depends(get_data_quality_service),
    state_store: StateStore = Depends(get_state_store)
):
    """
    Generates a comprehensive data quality report for the dataset associated
    with the given session_id.
    """
    try:
        df = state_store.load_dataframe(session_id=request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for session_id: {request.session_id}")

        report = service.get_quality_report(df)
        # Explicitly convert the Pydantic model to a dict to match the response_model
        return report.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the quality report: {e}")
