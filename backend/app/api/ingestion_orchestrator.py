import os
import io
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Body
import pandas as pd
from pymongo import MongoClient
from pydantic import BaseModel, Field

# --- Constants and Configuration ---
# Define a secure, temporary directory for storing ingested files.
# This directory will be within a .tmp folder to signify its transient nature.
TEMP_STORAGE_PATH = Path("backend/data/.tmp/ingestion")
TEMP_STORAGE_PATH.mkdir(parents=True, exist_ok=True) # Ensure the directory exists

router = APIRouter(prefix="/ingestion", tags=["Ingestion Orchestrator"])

# --- Pydantic Schemas for Request Bodies ---
class MongoDbRequest(BaseModel):
    mongo_uri: str = Field(..., description="MongoDB connection URI.")
    db_name: str = Field(..., description="Name of the database.")
    collection_name: str = Field(..., description="Name of the collection.")

# --- Ingestion Orchestrator Service ---

class IngestionOrchestratorService:
    """
    Handles the entire data ingestion pipeline, from receiving files
    to processing and persisting them to a temporary storage.
    """

    def _save_to_temp_storage(self, df: pd.DataFrame) -> str:
        """
        Saves a DataFrame to a CSV file in the temporary storage area.
        Returns the unique ID of the saved file.
        """
        session_id = str(uuid.uuid4())
        output_folder = TEMP_STORAGE_PATH / session_id
        output_folder.mkdir(exist_ok=True)

        output_path = output_folder / "ingestion_result.csv"
        df.to_csv(output_path, index=False)

        return session_id

    async def process_single_file(self, file: UploadFile) -> str:
        """
        Processes a single uploaded file (e.g., CSV, Excel) and persists it.
        Returns a session_id pointing to the processed data.
        """
        # Note: This is a simplified version. The full implementation will
        # consolidate all the logic from the legacy and MPA loaders here.
        try:
            contents = await file.read()
            if file.content_type == "text/csv":
                df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
            elif file.content_type in [
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ]:
                # Simplified: assumes first sheet. Full version will handle multi-sheet.
                df = pd.read_excel(io.BytesIO(contents))
            else:
                raise HTTPException(status_code=415, detail="File type not supported in this version.")

            session_id = self._save_to_temp_storage(df)
            return session_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    def process_mongodb_source(self, request: MongoDbRequest) -> str:
        """
        Connects to a MongoDB source, ingests the data, and persists it.
        Returns a session_id pointing to the processed data.
        """
        try:
            client = MongoClient(request.mongo_uri)
            db = client[request.db_name]
            collection = db[request.collection_name]
            data = list(collection.find())
            client.close()

            if not data:
                raise HTTPException(status_code=404, detail="No documents found in the specified MongoDB collection.")

            df = pd.DataFrame(data)
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)

            session_id = self._save_to_temp_storage(df)
            return session_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing MongoDB source: {str(e)}")


# --- API Endpoints ---

@router.post("/upload/unified")
async def unified_upload(file: UploadFile = File(...)):
    """
    The new, unified endpoint for file ingestion.
    This endpoint accepts a file, processes it, persists it to a temporary
    location on the server, and returns a session_id for future reference.
    It DOES NOT return the data in the response.
    """
    service = IngestionOrchestratorService()
    session_id = await service.process_single_file(file)

    return {
        "message": "File processed and persisted successfully.",
        "session_id": session_id,
        "filename": file.filename
    }

@router.post("/ingest/mongodb")
async def ingest_from_mongodb(request: MongoDbRequest = Body(...)):
    """
    The new, unified endpoint for MongoDB ingestion.
    Connects to the database, persists the data, and returns a session_id.
    """
    service = IngestionOrchestratorService()
    session_id = service.process_mongodb_source(request)

    return {
        "message": "Data from MongoDB processed and persisted successfully.",
        "session_id": session_id,
        "source": f"MongoDB: {request.db_name}/{request.collection_name}"
    }
