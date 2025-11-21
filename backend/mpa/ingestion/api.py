import uuid
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

@router.post("/multi-upload/")
async def multi_upload(
    files: list[UploadFile] = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Handles multiple file uploads, processes them, and returns a task ID.
    NOTE: This is a simplified, synchronous version for interoperability.
    A full implementation would use a background task.
    """
    # In a real scenario, you would start a Celery task here:
    # task = process_files_task.delay([file.filename for file in files])
    # For now, we simulate a task ID and process synchronously.
    task_id = f"task_{uuid.uuid4()}"

    processed_files = []
    for file in files:
        df = await ingestion_service.process_file(file)
        processed_files.append({
            "filename": file.filename,
            "records": len(df)
        })

    return {
        "task_id": task_id,
        "status": "SUCCESS", # Simulating immediate success
        "message": f"{len(processed_files)} files processed.",
        "processed_files": processed_files
    }
