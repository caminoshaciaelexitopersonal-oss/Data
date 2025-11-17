from fastapi import APIRouter, HTTPException, Body, Depends, Security
from fastapi.security import APIKeyHeader
from typing import Dict, Any
import uuid

from backend.mcp.schemas import (
    SessionStartRequest,
    ChatRequest,
    EtlRequest,
    SessionResponse,
    ChatResponse
)

# --- MCP State ---
# A simple in-memory dictionary to store session data.
# In a real-world scenario, this would be a more robust storage like Redis or a database.
sessions: Dict[str, Any] = {}

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
async def create_session(request: SessionStartRequest):
    """
    Starts a new analysis session and stores the initial data.
    """
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"data": request.data}
    return {"session_id": session_id, "message": "Session created successfully."}

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
async def session_etl(session_id: str, request: EtlRequest):
    """
    Applies an ETL pipeline to the session's data.
    (Placeholder - will invoke the ETL MPA)
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Placeholder: In the future, this will call the MPA-ETL
    print(f"Applying {len(request.steps)} ETL steps to session {session_id}")
    return {"message": "ETL pipeline applied (placeholder)."}

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
