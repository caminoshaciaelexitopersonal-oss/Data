from typing import Dict, Optional
from uuid import UUID
from backend.mcp.schemas import Session, Job, Step

class McpService:
    """
    Service for the Main Control Plane (MCP).
    Handles the orchestration of sessions, jobs, and steps.
    Uses an in-memory dictionary for temporary persistence.
    """
    def __init__(self):
        self._sessions: Dict[UUID, Session] = {}

    def create_session(self) -> Session:
        """Creates a new analysis session."""
        new_session = Session()
        self._sessions[new_session.session_id] = new_session
        return new_session

    def get_session(self, session_id: UUID) -> Optional[Session]:
        """Retrieves a session by its ID."""
        return self._sessions.get(session_id)

    def create_job(self, session_id: UUID, job_type: str) -> Optional[Job]:
        """Creates a new job within a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        new_job = Job(session_id=session_id, type=job_type)
        session.jobs[new_job.job_id] = new_job
        return new_job

    def create_step(self, job_id: UUID, description: str, payload: Optional[Dict] = None) -> Optional[Step]:
        """Creates a new step within a job."""
        # This is inefficient for a real system, but fine for in-memory persistence.
        for session in self._sessions.values():
            if job_id in session.jobs:
                job = session.jobs[job_id]
                new_step = Step(job_id=job_id, description=description, payload=payload)
                job.steps[new_step.step_id] = new_step
                return new_step
        return None

# Create a singleton instance for dependency injection
mcp_service = McpService()

def get_mcp_service() -> McpService:
    return mcp_service
