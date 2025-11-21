from fastapi import APIRouter, Depends, Body
from typing import Dict, Any

from backend.wpa.db_ingestion.schemas import DbIngestionRequest, DbIngestionResponse
from backend.wpa.db_ingestion.service import DbIngestionService
from backend.mpa.ingestion.service import IngestionService, ingestion_service
from backend.audit.service import AuditService, audit_service
from backend.wpa.session_manager import session_manager

router = APIRouter(prefix="/wpa/ingestion", tags=["WPA - DB Ingestion"])

def get_db_ingestion_service():
    # The WPA service is composed of the required MPA and session manager services
    return DbIngestionService(ingestion_service=ingestion_service, session_manager=session_manager)

@router.post("/from-db", response_model=DbIngestionResponse)
async def ingest_from_db_endpoint(
    request: DbIngestionRequest,
    db_ingestion_service: DbIngestionService = Depends(get_db_ingestion_service),
    audit: AuditService = Depends(lambda: audit_service)
):
    audit.log_event("wpa_db_ingestion_started", request.job_id)
    try:
        result = db_ingestion_service.ingest_from_db(request)
        audit.log_event("wpa_db_ingestion_completed", request.job_id, details={"session_id": result["session_id"]})
        return DbIngestionResponse(
            job_id=request.job_id,
            message="Data ingested successfully from database.",
            **result
        )
    except Exception as e:
        audit.log_event("wpa_db_ingestion_failed", request.job_id, status="failed", details={"error": str(e)})
        raise

@router.post("/from-mongodb")
async def ingest_from_mongodb(
    mongo_uri: str = Body(...),
    db_name: str = Body(...),
    collection_name: str = Body(...)
) -> Dict[str, Any]:
    """Simulated endpoint for MongoDB data ingestion."""
    print(f"MongoDB connection request: {mongo_uri}, {db_name}, {collection_name}")
    # Simulate a successful data load
    return {
        "data": [
            {"_id": "mongo1", "product": "Laptop", "price": 1200},
            {"_id": "mongo2", "product": "Mouse", "price": 25}
        ]
    }

@router.post("/from-s3")
async def ingest_from_s3(
    bucket_name: str = Body(...),
    object_key: str = Body(...)
) -> Dict[str, Any]:
    """Simulated endpoint for S3 data ingestion."""
    print(f"S3 connection request: {bucket_name}, {object_key}")
    # Simulate a successful data load
    return {
        "data": [
            {"s3_item": "data.csv", "size_kb": 1024},
            {"s3_item": "backup.zip", "size_kb": 20480}
        ]
    }
