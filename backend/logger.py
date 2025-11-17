# backend/logger.py
import logging
import json
from typing import List, Dict, Any
from datetime import datetime

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
        # Add extra fields if they exist
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)

        # Add exception info if it exists
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def setup_logger() -> logging.Logger:
    """
    Sets up a logger that outputs structured JSON.
    """
    logger = logging.getLogger("sadi_logger")
    logger.setLevel(logging.INFO)

    # Prevents adding handlers multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# Initialize the logger
logger = setup_logger()


# --- In-memory step tracking for SADI Code Viewer ---
# This list remains to support the frontend's "View Code" feature.
executed_steps: List[Dict[str, Any]] = []

def log_step(
    description: str,
    code: str,
    llm_prompt: str = None,
    llm_response: str = None,
    execution_time_ms: float = None
):
    """
    Records an execution step for the SADI Code Viewer and also logs the event
    to the structured logger.
    """
    timestamp = datetime.utcnow().isoformat()

    # Log the event using the structured logger
    logger.info("Executing agent step", extra={'extra_data': {
        "event_type": "agent_step",
        "step_description": description,
        "execution_time_ms": execution_time_ms,
    }})

    # Keep the original functionality for the frontend Code Viewer
    log_entry = {
        "description": description,
        "code": code,
        "timestamp": timestamp,
        "llm_prompt": llm_prompt,
        "llm_response": llm_response,
        "execution_time_ms": execution_time_ms
    }
    executed_steps.append(log_entry)

def get_logged_steps() -> List[Dict[str, Any]]:
    """
    Returns all the steps that have been recorded for the SADI Code Viewer.
    """
    return executed_steps

def clear_log():
    """
    Clears the in-memory log of steps for the SADI Code Viewer.
    """
    logger.info("Clearing execution step log for new agent run.", extra={'extra_data': {"event_type": "log_clear"}})
    executed_steps.clear()
