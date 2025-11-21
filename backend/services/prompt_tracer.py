import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class PromptTracerService:
    """
    Service to trace and log prompts and their corresponding responses from the AI agent.
    """
    _log_dir = Path("data/logs/prompts/")

    def __init__(self):
        # Ensure the log directory exists
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def log_prompt(
        self,
        session_id: str,
        prompt: str,
        response: Dict[str, Any],
        model_used: str = "unknown",
        execution_time: float = -1.0
    ) -> str:
        """
        Logs the details of a prompt-response interaction to a session-specific JSON file.

        Args:
            session_id (str): The ID of the current user session.
            prompt (str): The user's input prompt.
            response (Dict[str, Any]): The structured response from the agent.
            model_used (str): The name of the LLM used for the response.
            execution_time (float): The time taken to generate the response.

        Returns:
            str: The unique ID of the trace log entry.
        """
        trace_id = f"trace_{uuid.uuid4()}"

        log_entry = {
            "trace_id": trace_id,
            "timestamp_utc": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "model_used": model_used,
            "execution_time_seconds": round(execution_time, 4),
            "prompt": prompt,
            "response": response,
        }

        session_log_file = self._log_dir / f"session_{session_id}.jsonl"

        try:
            with open(session_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            return trace_id
        except IOError as e:
            # In a real-world scenario, you might use a more robust logger here
            print(f"Error writing to prompt trace log: {e}")
            return ""

def get_prompt_tracer_service() -> PromptTracerService:
    """Dependency injector for the PromptTracerService."""
    return PromptTracerService()
