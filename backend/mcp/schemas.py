from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from uuid import UUID, uuid4

# --- Base Models for Traceability ---

class TraceableRequest(BaseModel):
    """
    Base model for all requests to ensure traceability.
    """
    job_id: UUID = Field(default_factory=uuid4)
    user_id: Optional[str] = "default_user" # Placeholder until auth is real

# --- Schemas for Core MCP Operations ---

class DbConnectionRequest(BaseModel):
    """
    Schema for database connection details, similar to the legacy one.
    """
    db_uri: str
    query: str

class SessionStartRequest(TraceableRequest):
    """
    Request model to start a new analysis session.
    Can be initiated with file data, a DB connection, or an API source.
    """
    source_type: Literal["file", "db", "api"]
    data: Optional[List[Dict[str, Any]]] = None
    db_connection: Optional[DbConnectionRequest] = None
    # api_details: Optional[ApiConnectionRequest] = None # For future use

class EtlStep(BaseModel):
    """
    A more strictly defined schema for a single step in an ETL pipeline.
    """
    action: Literal["rename", "drop_nulls", "fill_nulls"]
    parameters: Dict[str, Any]

class EtlRequest(TraceableRequest):
    """
    Request model for running an ETL pipeline on the session's data.
    """
    steps: List[EtlStep]

class ChatRequest(TraceableRequest):
    """
    Request model for sending a message to the agent within a session.
    """
    message: str

# --- Schemas for MPA-specific Jobs ---

class ModelTrainRequest(TraceableRequest):
    """
    Schema for a request to train a model.
    """
    model_type: Literal["random_forest", "svm", "decision_tree"]
    target: str
    features: List[str]
    experiment_name: str = "default_experiment"

class ModelPredictRequest(TraceableRequest):
    """
    Schema for a request to make predictions with a trained model.
    """
    run_id: str # MLflow run ID
    data: List[Dict[str, Any]]

class ReportGenerationRequest(TraceableRequest):
    """
    Schema for a request to generate a report.
    """
    summary: str
    include_visualizations: bool = True

# --- Response Schemas ---

class SessionResponse(BaseModel):
    session_id: str
    job_id: UUID
    message: str

class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    message: str

class ReportResponse(BaseModel):
    report_id: str
    job_id: UUID
    download_url: str
    message: str
