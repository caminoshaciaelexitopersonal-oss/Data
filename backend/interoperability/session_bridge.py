# backend/interoperability/session_bridge.py

"""
Session Bridge for the Interoperability Layer.

This module's primary responsibility is to solve the critical issue of
MCP's in-memory, volatile persistence. It will bridge session and job
management calls to the stable, file-based legacy StateStore.
"""

import uuid
from backend.app.services.state_store import StateStore, get_state_store

class SessionBridge:
    """
    Translates MCP session operations to use the legacy StateStore.
    """
    def __init__(self, state_store: StateStore = get_state_store()):
        self._state_store = state_store

    def bridge_create_session(self):
        """
        Handles the creation of a session, ensuring it is persisted
        in the legacy StateStore instead of the MCP's in-memory dictionary.
        """
        # Generate a new session ID
        session_id = str(uuid.uuid4())

        # Use the persistent state store to create the session
        self._state_store.create_session(session_id)

        # For now, manually log the audit event. Later, this could be a decorator.
        from .controller import get_interop_controller
        get_interop_controller()._log_audit_event(
            endpoint_name="/session/create",
            details=f"Persisted new session with ID: {session_id}"
        )

        # Return a response consistent with the expected format
        return {
            "message": "Session created and persisted via Interoperability Bridge.",
            "session_id": session_id,
            "persistence_mode": "stable"
        }

# Singleton instance for the session bridge
# The dependency is resolved at instantiation time.
session_bridge = SessionBridge()

def get_session_bridge() -> SessionBridge:
    return session_bridge
