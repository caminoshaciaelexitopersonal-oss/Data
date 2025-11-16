import pytest
import json
from pathlib import Path
from backend.app.services import audit_service

@pytest.fixture
def temp_audit_log(tmp_path: Path) -> Path:
    """Fixture to create a temporary audit log file for testing."""
    temp_file = tmp_path / "test_audit_log.json"
    audit_service.AUDIT_LOG_PATH = temp_file
    return temp_file

def test_write_single_audit_log_entry(temp_audit_log: Path):
    """Tests that a single entry can be written to a new log file."""
    entry = {"event": "test", "status": "success"}
    audit_service.write_audit_log(entry)
    with open(temp_audit_log, "r") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["event"] == "test"

def test_write_multiple_audit_log_entries(temp_audit_log: Path):
    """Tests that multiple entries are correctly appended as a JSON array."""
    audit_service.write_audit_log({"event": "start"})
    audit_service.write_audit_log({"event": "finish"})
    with open(temp_audit_log, "r") as f:
        data = json.load(f)
    assert len(data) == 2

def test_save_code_block(tmp_path: Path):
    """Tests that a code block is saved to the correct location."""
    audit_service.CODE_BLOCKS_PATH = tmp_path
    job_id = "test_job_123"
    snippet = "print('hello world')"
    meta = {"step": "test_step"}
    audit_service.save_code_block(job_id, snippet, meta)
    job_path = tmp_path / job_id
    saved_files = list(job_path.glob("test_step_*.py"))
    assert len(saved_files) == 1
    assert saved_files[0].read_text() == snippet
