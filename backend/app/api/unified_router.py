# backend/app/api/unified_router.py

"""
The Unified API Router for SADI.

This router serves as the single, stable entry point for all frontend operations.
It completely decouples the client from the complex and conflicting backend architectures.

Each endpoint defined here will delegate its logic to the InteropController,
which will then use the appropriate bridge to fulfill the request.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Body, Request, HTTPException, Form
from backend.interoperability.controller import InteropController, get_interop_controller
import pandas as pd

router = APIRouter(prefix="/unified/v1", tags=["Unified Stable Endpoints"])

# NOTE: The implementation of these endpoints is intentionally minimal.
# They are simple pass-throughs to the interoperability controller,
# which holds the responsibility of orchestrating the complex logic.

from backend.interoperability.data_bridge import DataBridge, get_data_bridge

@router.post("/ingestion/upload-file")
async def unified_ingestion(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    data_bridge: DataBridge = Depends(get_data_bridge)
):
    """
    Unified endpoint for file ingestion. Always persistent.
    """
    # DELEGATION: This endpoint now directly calls the data bridge.
    return await data_bridge.bridge_ingestion(file, session_id)

from backend.interoperability.session_bridge import SessionBridge, get_session_bridge

@router.post("/session/create")
async def unified_create_session(
    session_bridge: SessionBridge = Depends(get_session_bridge)
):
    """
    Unified endpoint for creating a session. Always persistent.
    """
    # DELEGATION: This endpoint now directly calls the session bridge.
    return session_bridge.bridge_create_session()

@router.post("/chat/agent")
async def unified_chat_agent(
    request: Request,
    controller: InteropController = Depends(get_interop_controller)
):
    """
    Unified endpoint for the chat agent.
    """
    # In FASE 3, this will call:
    # payload = await request.json()
    # return await controller.bridge_chat(payload)
    return {"message": "Unified chat agent endpoint is active", "status": "pending_implementation"}

from backend.services.data_quality_service import DataQualityService, get_data_quality_service
from pathlib import Path

TEMP_STORAGE_PATH = Path("backend/data/.tmp/ingestion")

@router.post("/quality/report")
async def unified_quality_report(
    session_id: str = Body(..., embed=True),
    service: DataQualityService = Depends(get_data_quality_service)
):
    """
    Unified endpoint for generating a data quality report from a session_id.
    """
    file_path = TEMP_STORAGE_PATH / session_id / "ingestion_result.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="No data found for the given session ID.")

    df = pd.read_csv(file_path)
    report = service.get_quality_report(df)
    return report

# Additional unified endpoints for EDA, quality, ML, etc., will be added here.
