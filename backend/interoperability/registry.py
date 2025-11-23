# backend/interoperability/registry.py

"""
Service and Endpoint Registry for the Interoperability Layer.

This module will maintain a mapping of unified endpoint definitions to their
actual implementations in either the legacy or the new architecture. This allows
the InteropController to dynamically dispatch requests without hardcoding routes.
"""

class EndpointRegistry:
    """
    Provides a centralized registry of available endpoints from both
    legacy and new architectures.
    """
    def __init__(self):
        self._registry = {
            "unified/v1/ingestion": {
                "legacy": "ingestion_orchestrator.unified_upload",
                "mpa": "mpa.ingestion.upload_file",
                "bridge": "data_bridge.bridge_ingestion"
            },
            "unified/v1/sessions": {
                "mcp": "mcp.api.create_session",
                "bridge": "session_bridge.bridge_create_session"
            }
            # More endpoints will be registered here.
        }

    def get_endpoint_implementations(self, unified_route: str):
        """
        Retrieves the available implementations for a given unified route.
        """
        return self._registry.get(unified_route)

# Singleton instance for the registry
endpoint_registry = EndpointRegistry()

def get_endpoint_registry() -> EndpointRegistry:
    return endpoint_registry
