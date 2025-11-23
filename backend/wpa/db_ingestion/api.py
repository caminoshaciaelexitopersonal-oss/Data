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

