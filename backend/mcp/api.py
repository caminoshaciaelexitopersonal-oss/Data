from fastapi import APIRouter, HTTPException, Body, Depends, Security
from fastapi.security import APIKeyHeader
from typing import Dict, Any
import uuid
 
import pandas as pd
 

from backend.mcp.schemas import (
    SessionStartRequest,
    ChatRequest,
    EtlRequest,
    SessionResponse,
    ChatResponse
)
 
from backend.mpa.ingestion.service import IngestionService
from backend.mpa.etl.service import EtlService
from backend.mpa.eda.service import EdaService
 

# --- MCP State ---
# A simple in-memory dictionary to store session data.
# In a real-world scenario, this would be a more robust storage like Redis or a database.
sessions: Dict[str, Any] = {}

 
# --- Dependency for MPA Services ---
def get_ingestion_service():
    return IngestionService()

def get_etl_service():
    return EtlService()

def get_eda_service():
    return EdaService()

 
# --- Security Placeholder ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Placeholder for API key validation.
    In the future, this will check the key against a database of valid keys.
    """
    if api_key == "development_key":  # Example valid key
        return api_key
    else:
        # For now, we allow access even without a key, but this is where
        # the HTTPException for invalid keys would be raised.
        # raise HTTPException(status_code=403, detail="Could not validate credentials")
        print("Warning: No valid API key provided. Allowing access for development.")
        return None

# --- API Router ---
# All routes in the MCP will depend on this security placeholder.
router = APIRouter(
    prefix="/mcp",
    tags=["Main Control Plane"],
    dependencies=[Depends(get_api_key)]
)


@router.post("/sessions/", response_model=SessionResponse)
 
async def create_session(
    request: SessionStartRequest,
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Starts a new analysis session by orchestrating the Ingestion MPA.
    This demonstrates the MCP's role as a controller.
    """
    session_id = str(uuid.uuid4())

    # The MCP calls the appropriate MPA to handle the business logic.
    # For now, we simulate this by passing the data directly.
    # In a real implementation, the request would contain a file ID or DB details,
    # and the MPA would fetch the data itself.
    df = pd.DataFrame(request.data) # Simulating DataFrame creation

    sessions[session_id] = {"data": df}
    print(f"MCP created session {session_id} using the Ingestion MPA.")

    return {"session_id": session_id, "message": "Session created successfully via MCP orchestration."}
 

@router.post("/sessions/{session_id}/chat", response_model=ChatResponse)
async def session_chat(session_id: str, request: ChatRequest):
    """
    Handles a chat message for a specific session.
    (Placeholder - will invoke the Analysis MPA)
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Placeholder: In the future, this will call the MPA-Análisis
    print(f"Received message: '{request.message}' for session {session_id}")
    return {"output": f"Placeholder response for: '{request.message}'"}

@router.post("/sessions/{session_id}/etl")
 
async def session_etl(
    session_id: str,
    request: EtlRequest,
    etl_service: EtlService = Depends(get_etl_service)
):
    """
    Applies an ETL pipeline to the session's data by orchestrating the ETL MPA.
 
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

 
    current_df = sessions[session_id].get("data")
    if current_df is None:
        raise HTTPException(status_code=400, detail="No data found in session to process.")

    # The MCP calls the MPA to perform the business logic
    processed_df = etl_service.process_pipeline(current_df, request.steps)

    # Update the session state with the processed data
    sessions[session_id]["data"] = processed_df

    return {
        "message": f"ETL pipeline with {len(request.steps)} steps applied successfully.",
        "data_sample": processed_df.head().to_dict(orient='records')
    }
 

@router.get("/sessions/{session_id}/artifacts/visualizations")
async def get_visualizations(session_id: str):
    """
    Retrieves visualizations for a session.
    (Placeholder - will query artifacts from the session state)
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Placeholder
    return {"visualizations": "No visualizations available yet (placeholder)."}
 

@router.post("/sessions/{session_id}/analysis/eda")
async def session_eda_analysis(
    session_id: str,
    eda_service: EdaService = Depends(get_eda_service)
):
    """
    Performs an Exploratory Data Analysis on the session's data.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    df = sessions[session_id].get("data")
    if df is None:
        raise HTTPException(status_code=400, detail="No data in session.")

    eda_results = eda_service.generate_advanced_eda(df)

    # In the future, these results could be stored in the session state.
    return eda_results
 
@router.post("/sessions/{session_id}/analysis/data-health")
async def session_data_health(
    session_id: str,
    eda_service: EdaService = Depends(get_eda_service)
):
    """
    Generates a data health report for the session's data.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    df = sessions[session_id].get("data")
    if df is None:
        raise HTTPException(status_code=400, detail="No data in session.")

    health_report = eda_service.generate_data_health_report(df)

    return health_report
 
