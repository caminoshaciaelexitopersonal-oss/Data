from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime

# Base model for traceability that WPA schemas depend on
class TraceableRequest(BaseModel):
    job_id: UUID = Field(default_factory=uuid4)
    user_id: Optional[str] = None

# Model for ETL steps that WPA schemas depend on
class EtlStep(BaseModel):
    action: str
    params: Dict[str, Any]

class Session(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"
    jobs: Dict[UUID, "Job"] = {}

class Job(BaseModel):
    job_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"
    steps: Dict[UUID, "Step"] = {}

class Step(BaseModel):
    step_id: UUID = Field(default_factory=uuid4)
    job_id: UUID
    description: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"

# Update forward references for self-referencing models
Session.update_forward_refs()
Job.update_forward_refs()
