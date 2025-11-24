from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any
from pydantic import BaseModel

from backend.services.eda_intelligent_service import EdaIntelligentService, get_eda_intelligent_service
from backend.app.services.state_store import StateStore, get_state_store

router = APIRouter(prefix="/mpa/eda", tags=["MPA - EDA"])

class SessionRequest(BaseModel):
    """Defines the standard request model for session-based operations."""
    session_id: str

@router.post("/intelligent", response_model=Dict[str, Any])
def run_intelligent_eda(
    request: SessionRequest = Body(...),
    service: EdaIntelligentService = Depends(get_eda_intelligent_service),
    state_store: StateStore = Depends(get_state_store)
):
    """
    Runs a full suite of intelligent EDA tools on the dataset associated
    with the given session_id.
    """
    try:
        # Load the DataFrame from the state store using the session_id
        df = state_store.load_dataframe(session_id=request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for session_id: {request.session_id}")

        # Execute all intelligent EDA functions on the loaded data
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
