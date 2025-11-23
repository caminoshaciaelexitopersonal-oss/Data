# backend/audit/persistent_logger.py
import json
from datetime import datetime

class PersistentLogger:
    """
    A simple logger to persist agent steps, as required by the restoration plan.
    """
    _log_file = "persistent_agent_log.jsonl"

    def log_step(self, session_id: str, step_name: str, details: dict):
        """
        Logs a step to a persistent JSONL file.
        """
        log_entry = {
            "session_id": session_id,
            "step_name": step_name,
            "details": details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        try:
            with open(self._log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Failed to write to persistent log: {e}")
