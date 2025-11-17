from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

from backend.mcp.schemas import TraceableRequest

class ReportGenerationRequest(TraceableRequest):
    """
    Request model to generate a report.
    """
    title: str
    summary: str
    # This would eventually come from the session/job artifacts
    visualization_keys: Optional[List[str]] = None

class ReportGenerationResponse(BaseModel):
    """
    Response model after generating a report.
    """
    job_id: UUID
    message: str
    report_url: str # A URL to download the report
