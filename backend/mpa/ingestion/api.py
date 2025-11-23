import uuid
from fastapi import APIRouter, File, UploadFile, Depends, Form
from backend.mpa.ingestion.service import IngestionService

# --- API Router for Ingestion MPA ---
router = APIRouter(prefix="/mpa/ingestion", tags=["MPA - Ingestion"])

# --- Dependency Injection for the Service ---
def get_ingestion_service():
    return IngestionService()

@router.post("/upload-file/")
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Handles file uploads and processes them using the IngestionService.
    This is the new MPA-based endpoint for file ingestion.
    """
    df = await ingestion_service.process_file(file, session_id)
    # Return filename and a confirmation message, not the full data.
    return {
        "filename": file.filename,
        "message": f"File processed and associated with session {session_id}."
    }

