from typing import Dict, Optional
from uuid import UUID, uuid4
from backend.mcp.schemas import Session, Job, Step
from backend.app.services.state_store import StateStore, get_state_store

class McpService:
    """
    Service for the Main Control Plane (MCP).
    Handles the orchestration of sessions, jobs, and steps.
    Uses a persistent StateStore instead of in-memory dictionaries.
    """
    def __init__(self, state_store: StateStore):
        self._store = state_store

    def create_session(self) -> Session:
        """Creates a new analysis session."""
        new_session_schema = Session()
        self._store.create_session(str(new_session_schema.session_id))
        return new_session_schema

    def get_session(self, session_id: UUID) -> Optional[Session]:
        """Retrieves a session by its ID from the persistent store."""
        session_data = self._store.get_session(str(session_id))
        if not session_data:
            return None
        # Reconstruct the Pydantic model from the dictionary
        return Session.parse_obj(session_data)

    def create_job(self, session_id: UUID, job_type: str) -> Optional[Job]:
        """Creates a new job within a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        new_job_schema = Job(session_id=session_id, type=job_type)
        self._store.create_job(
            session_id=str(session_id),
            job_id=str(new_job_schema.job_id),
            job_type=new_job_schema.type
        )
        return new_job_schema

    def create_step(self, job_id: UUID, description: str, payload: Optional[Dict] = None) -> Optional[Step]:
        """Creates a new step within a job."""
        job_data = self._store.get_job(str(job_id))
        if not job_data:
            return None

        new_step_schema = Step(job_id=job_id, description=description, payload=payload)
        self._store.create_mcp_step(
            step_id=str(new_step_schema.step_id),
            job_id=str(job_id),
            description=description,
            payload=payload
        )
        return new_step_schema

# --- Dependency Injection ---

# Keep a singleton instance to be injected
mcp_service = McpService(get_state_store())

def get_mcp_service() -> McpService:
    return mcp_service
