import json
import fcntl
import time
from pathlib import Path
from typing import Dict, Any

AUDIT_LOG_PATH = Path("data/logs/audit_log.json")
CODE_BLOCKS_PATH = Path("data/processed/code_blocks")

def write_audit_log(entry: Dict[str, Any]):
    """Appends a new entry to the audit log in a thread-safe and safe manner using r+ mode."""
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.write_text("[]\n")

    with open(AUDIT_LOG_PATH, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0, 2)
        position = f.tell()
        f.seek(position - 2)
        if position > 3:
            f.write(",\n")
        else:
            f.seek(1)
        json.dump(entry, f, indent=2)
        f.write("\n]\n")
        fcntl.flock(f, fcntl.LOCK_UN)

def save_code_block(job_id: str, snippet: str, meta: Dict[str, Any]):
    """Saves a code snippet to a file within the job's directory."""
    step = meta.get("step", "unknown_step")
    timestamp = int(time.time())
    job_path = CODE_BLOCKS_PATH / job_id
    job_path.mkdir(parents=True, exist_ok=True)
    file_path = job_path / f"{step}_{timestamp}.py"
    file_path.write_text(snippet)
