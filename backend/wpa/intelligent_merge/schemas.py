from pydantic import BaseModel
from typing import List, Dict

class IntelligentMergeResponse(BaseModel):
    """
    Response schema for the intelligent merge workflow.
    """
    message: str
    quality_report_path: str
    exported_files: Dict[str, str] # e.g., {"csv": "/path/to/file.csv"}
    log_file_path: str
