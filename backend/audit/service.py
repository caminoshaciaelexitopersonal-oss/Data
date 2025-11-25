import json
import uuid
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any

class AuditService:
    """
    A centralized service for logging audit trails of all significant events
    in the MCP and other parts of the system.
    """
    _log_file = "audit_log.json"

    def log_event(
        self,
        event_name: str,
        job_id: UUID,
        user_id: Optional[str] = "default_user",
        session_id: Optional[str] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Logs a structured event to the audit log file.

        Args:
            event_name (str): The name of the event (e.g., "session_created", "model_trained").
            job_id (UUID): The unique ID of the job this event belongs to.
            user_id (str, optional): The ID of the user who initiated the event.
            session_id (str, optional): The session ID if the event is part of a session.
            status (str, optional): The status of the event (e.g., "success", "failed", "pending").
            details (Dict[str, Any], optional): Any additional structured data about the event.
        """
        log_entry = {
            "audit_id": str(uuid.uuid4()),
            "job_id": str(job_id),
            "user_id": user_id,
            "session_id": session_id,
            "event_name": event_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": status,
            "details": details or {}
        }

        try:
            with open(self._log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            # In a real application, this should go to a more robust logging system
            print(f"Failed to write to audit log: {e}")

# Instantiate the service for dependency injection
audit_service = AuditService()
