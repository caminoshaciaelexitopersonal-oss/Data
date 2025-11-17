from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SessionStartRequest(BaseModel):
    """
    Request model to start a new analysis session.
    Can be initiated with either file data (for uploads) or a DB connection.
    """
    # For now, we'll keep it simple and assume data is passed directly.
    # In the future, this could point to a file ID or DB connection details.
    data: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    """
    Request model for sending a message to the agent within a session.
    """
    message: str

class EtlRequest(BaseModel):
    """
    Request model for running an ETL pipeline on the session's data.
    """
    steps: List[Dict[str, Any]]

class SessionResponse(BaseModel):
    """
    Response model for a newly created session.
    """
    session_id: str
    message: str

class ChatResponse(BaseModel):
    """
    Response model for a message processed by the agent.
    """
    output: Any
