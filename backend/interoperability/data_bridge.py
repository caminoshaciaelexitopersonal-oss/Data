# backend/interoperability/data_bridge.py

"""
Data Bridge for the Interoperability Layer.

This module is responsible for bridging the data ingestion functionalities.
Specifically, it will adapt the new, non-persistent MPA ingestion endpoint
to use the robust, persistent logic of the legacy IngestionOrchestrator.
"""

from backend.app.api.ingestion_orchestrator import IngestionOrchestratorService

class DataBridge:
    """
    Translates and unifies data-related operations.
    """
    def __init__(self):
        # The service is instantiated on demand, consistent with legacy approach.
        self._ingestion_service = IngestionOrchestratorService()

    async def bridge_ingestion(self, file, session_id: str):
        """
        Bridges the MPA file upload to the legacy persistent storage pattern.

        1. Receives a file and session_id from a unified endpoint.
        2. Calls the IngestionOrchestrator to process and save the file
           under the given session_id.
        3. Returns a consistent response.
        """
        await self._ingestion_service.process_single_file(file, session_id)

        # Log the audit event
        from .controller import get_interop_controller
        get_interop_controller()._log_audit_event(
            endpoint_name="/ingestion/upload-file",
            details=f"Persisted file '{file.filename}' to session ID: {session_id}"
        )

        return {
            "message": "File processed and persisted via Interoperability Bridge.",
            "session_id": session_id,
            "filename": file.filename,
            "persistence_mode": "stable"
        }

# Singleton instance for the data bridge
data_bridge = DataBridge()

def get_data_bridge() -> DataBridge:
    return data_bridge
