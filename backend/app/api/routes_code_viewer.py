from fastapi import APIRouter, HTTPException
from pathlib import Path
import os
from typing import List, Dict

router = APIRouter()
CODE_BLOCKS_PATH = Path("data/processed/code_blocks")

@router.get("/api/code_blocks/{job_id}", response_model=List[Dict[str, str]])
def get_code_blocks(job_id: str):
    job_path = CODE_BLOCKS_PATH / job_id
    if not job_path.is_dir():
        raise HTTPException(status_code=404, detail="Job not found.")
    blocks = []
    for file_path in sorted(job_path.iterdir()):
        if file_path.is_file() and file_path.suffix == '.py':
            blocks.append({"phase": file_path.name, "snippet": file_path.read_text()})
    return blocks
