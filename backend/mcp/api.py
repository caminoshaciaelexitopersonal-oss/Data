from fastapi import APIRouter, Depends, HTTPException, Body
from uuid import UUID
from typing import Optional, Dict

from backend.mcp.service import McpService, get_mcp_service
from backend.mcp.schemas import Session, Job, Step

router = APIRouter(tags=["MCP - Main Control Plane"])

@router.post("/session/create", response_model=Session)
def create_session(service: McpService = Depends(get_mcp_service)):
    """Creates a new analysis session."""
    return service.create_session()

@router.get("/session/{session_id}", response_model=Session)
def get_session(session_id: UUID, service: McpService = Depends(get_mcp_service)):
    """Retrieves a session by its ID."""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/job/start", response_model=Job)
def create_job(
    session_id: UUID = Body(..., embed=True),
    job_type: str = Body(..., embed=True),
    service: McpService = Depends(get_mcp_service)
):
    """Creates a new job within a session."""
    job = service.create_job(session_id, job_type)
    if not job:
        raise HTTPException(status_code=404, detail="Session not found to create job in")
    return job

@router.post("/step", response_model=Step)
def create_step(
    job_id: UUID = Body(..., embed=True),
    description: str = Body(..., embed=True),
    payload: Optional[Dict] = Body(None, embed=True),
    service: McpService = Depends(get_mcp_service)
):
    """Creates a new step within a job."""
    step = service.create_step(job_id, description, payload)
    if not step:
        raise HTTPException(status_code=404, detail="Job not found to create step in")
    return step

