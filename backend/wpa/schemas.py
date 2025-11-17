from pydantic import BaseModel
from typing import List, Dict, Any

from backend.mcp.schemas import TraceableRequest, EtlStep

class WpaAutoAnalysisRequest(TraceableRequest):
    """
    Request model for the Automated Analysis workflow.
    It contains the data source and the ETL steps to be applied.
    """
    source_type: str
    data: List[Dict[str, Any]]
    etl_steps: List[EtlStep]

class WpaAutoAnalysisResponse(BaseModel):
    """
    Response model for the Automated Analysis workflow.
    It returns the job_id for traceability and the final EDA report.
    """
    job_id: str
    message: str
    eda_report: Dict[str, Any]
