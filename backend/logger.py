# backend/logger.py
import logging
import json
from typing import List, Dict, Any
from datetime import datetime
from backend.app.services.state_store import get_state_store

# --- Structured Logger Setup ---

class JsonFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
        }
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger() -> logging.Logger:
    """
    Sets up a logger that outputs structured JSON.
    """
    logger = logging.getLogger("sadi_logger")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()

# --- Persistent Step Tracking using StateStore ---
# The in-memory list `executed_steps` has been removed.

def log_step(
    session_id: str,
    description: str,
    code: str,
    llm_prompt: str = None,
    llm_response: str = None,
    execution_time_ms: float = None
):
    """
    Records an execution step to the persistent StateStore and also logs
    the event to the structured logger.
    """
    logger.info("Executing agent step", extra={'extra_data': {
        "event_type": "agent_step",
        "step_description": description,
        "execution_time_ms": execution_time_ms,
    }})

    # Persist the step in the StateStore instead of the in-memory list.
    state_store = get_state_store()
    state_store.log_step(
        session_id=session_id,
        description=description,
        code=code
    )

def get_logged_steps(session_id: str) -> List[Dict[str, Any]]:
    """
    Returns all the steps for a given session from the persistent StateStore.
    """
    # Retrieve steps from the StateStore instead of the in-memory list.
    state_store = get_state_store()
    return state_store.get_steps(session_id=session_id)

# The `clear_log` function has been removed. Its functionality is incompatible
# with a persistent, multi-session state model.
