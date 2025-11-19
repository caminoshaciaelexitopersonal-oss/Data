from fastapi import APIRouter, File, UploadFile, Depends
from backend.mpa.ingestion.service import IngestionService

# --- API Router for Ingestion MPA ---
router = APIRouter(prefix="/mpa/ingestion", tags=["MPA - Ingestion"])

# --- Dependency Injection for the Service ---
def get_ingestion_service():
    return IngestionService()

@router.post("/upload-file/")
async def upload_file(
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Handles file uploads and processes them using the IngestionService.
    This is the new MPA-based endpoint for file ingestion.
    """
    df = await ingestion_service.process_file(file)
    # Return filename and the full data
    return {
        "filename": file.filename,
        "data": df.to_dict(orient="records"),
        "message": "File processed successfully by the Ingestion MPA."
    }
