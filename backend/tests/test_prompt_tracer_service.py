
import pytest
import json
from pathlib import Path
import time
from unittest.mock import patch

from backend.services.prompt_tracer import PromptTracerService

@pytest.fixture
def tracer_service(tmp_path):
    """Fixture to create a PromptTracerService with a temporary log directory."""
    # Mock the _log_dir to use a temporary directory provided by pytest's tmp_path fixture
    with patch.object(PromptTracerService, '_log_dir', tmp_path):
        service = PromptTracerService()
        # The service's __init__ should create the mocked directory
        assert service._log_dir.exists()
        yield service

def test_log_directory_creation(tmp_path):
    """Tests that the service creates the log directory if it doesn't exist."""
    log_dir = tmp_path / "new_logs"
    assert not log_dir.exists()
    with patch.object(PromptTracerService, '_log_dir', log_dir):
        PromptTracerService()
    assert log_dir.exists()

def test_log_prompt_creates_file_and_writes_log(tracer_service):
    """Tests that a log file is created and a correct log entry is written."""
    session_id = "test_session_123"
    prompt = "Analyze this data."
    response = {"output": "This is the analysis."}
    model = "test_model"
    exec_time = 0.1234

    tracer_service.log_prompt(session_id, prompt, response, model, exec_time)

    expected_file = tracer_service._log_dir / f"session_{session_id}.jsonl"
    assert expected_file.exists()

    with open(expected_file, "r", encoding="utf-8") as f:
        log_content = f.readline()
        log_data = json.loads(log_content)

    assert log_data["session_id"] == session_id
    assert log_data["prompt"] == prompt
    assert log_data["response"]["output"] == "This is the analysis."
    assert log_data["model_used"] == model
    assert log_data["execution_time_seconds"] == 0.1234
    assert "trace_id" in log_data
    assert "timestamp_utc" in log_data
