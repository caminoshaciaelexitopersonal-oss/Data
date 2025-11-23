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

from backend.schemas import ChatRequest
from backend.app.services.state_store import StateStore
from backend.interoperability.unified_agent import UnifiedAgent
from backend.audit.persistent_logger import PersistentLogger

@router.post("/chat/agent")
async def unified_chat_agent(payload: ChatRequest):
    """
    Unified endpoint for the chat agent.
    """
    session_id = payload.session_id
    message = payload.message

    # 1. Cargar sesión
    # NOTE: Direct instantiation as per restoration plan.
    session = StateStore().get_session(session_id)

    # 2. Enviar al agente unificado
    agent = UnifiedAgent(session=session)
    response = agent.run(message)

    # 3. Registrar paso
    PersistentLogger().log_step(session_id, "agent_response", response)

    return {"response": response}

from backend.schemas import SessionRequest

from backend.interoperability.mpa_controller import MpaController

# --- Functional Endpoints ---
# These endpoints are now connected to the UnifiedAgent, providing a consistent
# entry point for all analysis tasks.

@router.post("/quality/report")
async def unified_quality_report(payload: SessionRequest):
    """
    Generates a data quality report for the session by directly calling the MPA controller.
    """
    session = StateStore().get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    mpa_controller = MpaController(session)
    report = mpa_controller.execute_quality_report()
    return report

@router.post("/eda/report")
async def unified_eda_report(payload: SessionRequest):
    """
    Generates an Exploratory Data Analysis (EDA) report for the session.
    (Placeholder pending MPA service implementation)
    """
    return {"message": "EDA report endpoint is active", "status": "pending_implementation"}

@router.post("/ml/train")
async def unified_ml_train(payload: SessionRequest):
    """
    Trains a machine learning model based on the session data.
    (Placeholder pending MPA service implementation)
    """
    return {"message": "ML training endpoint is active", "status": "pending_implementation"}

@router.get("/visualizations")
async def unified_visualizations(session_id: str):
    """
    Retrieves all generated visualizations for the session.
    (Placeholder pending MPA service implementation)
    """
    return {"message": "Visualizations endpoint is active", "status": "pending_implementation"}
