from typing import List, Dict, Any
import uuid
from . import audit_service

def orchestrate_etl(sources: List[Dict[str, Any]]) -> str:
    """Orchestrates the ETL process."""
    job_id = str(uuid.uuid4())
    for source in sources:
        audit_entry = {"job_id": job_id, "file": source.get("name"), "status": "processing"}
        audit_service.write_audit_log(audit_entry)
    return job_id
