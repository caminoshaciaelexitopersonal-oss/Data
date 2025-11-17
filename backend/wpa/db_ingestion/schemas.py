from pydantic import BaseModel, Field
from typing import List, Dict, Any
from uuid import UUID

from backend.mcp.schemas import TraceableRequest

class DbIngestionRequest(TraceableRequest):
    """
    Request model for ingesting data from a database.
    """
    db_uri: str = Field(..., description="SQLAlchemy connection string (e.g., 'postgresql://user:pass@host/db')")
    sql_query: str

class DbIngestionResponse(BaseModel):
    """
    Response model after ingesting data from a database.
    """
    job_id: UUID
    message: str
    session_id: str # The session where the loaded data is stored
    data_preview: List[Dict[str, Any]]
