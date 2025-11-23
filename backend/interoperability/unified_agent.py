# backend/interoperability/unified_agent.py

"""
The Unified Agent for SADI.

This agent acts as the primary bridge between the stable, unified API layer
and the new, modular backend architecture (MCP, MPA, WPA).
"""

from backend.interoperability.mpa_controller import MpaController

# Placeholder imports for controllers. These will be replaced with actual
# service/controller imports as the implementation progresses.
# For now, we define placeholder classes to match the plan's structure.
class MCPController:
    def __init__(self, session):
        self.session = session
    def process_message(self, message: str) -> dict:
        print(f"MCP processing message for session {self.session['session_id']}: {message}")
        # Placeholder: a real implementation would use an LLM for intent detection.
        # For now, we hardcode the intent based on the message for testing.
        if "quality" in message:
            return {"intent": "run_quality_report", "parameters": {}}
        return {"intent": "run_eda", "parameters": {}} # Default fallback

class WPAController:
    def __init__(self, session):
        self.session = session
    def format_output(self, result: dict) -> dict:
        print(f"WPA formatting result for session {self.session['session_id']}: {result}")
        # The result from the real MPA is already a dict, so we can return it directly.
        return result

class UnifiedAgent:
    """
    Orchestrates the new architecture (MCP, MPA, WPA) to fulfill a user request.
    """
    def __init__(self, session):
        self.session = session
        self.mcp = MCPController(session)
        self.mpa = MpaController(session) # Using the real MPA Controller now
        self.wpa = WPAController(session)

    def run(self, message: str) -> dict:
        """
        Executes the full analysis pipeline.
        1. MCP determines user intent.
        2. MPA executes the core logic based on the intent.
        3. WPA formats the final output.
        """
        intent = self.mcp.process_message(message)

        # Route to the correct MPA method based on intent
        if intent.get("intent") == "run_quality_report":
            result = self.mpa.execute_quality_report()
        else:
            # Default fallback for other intents
            result = {"error": f"Intent '{intent.get('intent')}' not implemented yet."}

        final_output = self.wpa.format_output(result)
        return final_output
