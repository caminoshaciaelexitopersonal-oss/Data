from fastapi import APIRouter, Depends

from backend.wpa.schemas import WpaAutoAnalysisRequest, WpaAutoAnalysisResponse
from backend.wpa.auto_analysis.service import WpaAutoAnalysisService
from backend.mpa.ingestion.service import IngestionService
from backend.mpa.etl.service import EtlService
from backend.mpa.eda.service import EdaService
from backend.audit.service import AuditService

# --- API Router for WPA ---
router = APIRouter(prefix="/wpa", tags=["WPA - Workflow Process Automation"])

# --- Dependency Injection for Services ---
def get_wpa_auto_analysis_service():
    # This demonstrates how WPA services are composed of MPA services
    return WpaAutoAnalysisService(
        ingestion_service=IngestionService(),
        etl_service=EtlService(),
        eda_service=EdaService()
    )

def get_audit_service():
    return AuditService()

@router.post("/auto-analysis", response_model=WpaAutoAnalysisResponse)
async def auto_analysis(
    request: WpaAutoAnalysisRequest,
    wpa_service: WpaAutoAnalysisService = Depends(get_wpa_auto_analysis_service),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    Executes the automated data analysis workflow (Ingestion -> ETL -> EDA).
    """
    audit_service.log_event("wpa_auto_analysis_started", request.job_id, request.user_id)
    try:
        eda_report = wpa_service.execute(request)

        audit_service.log_event("wpa_auto_analysis_completed", request.job_id, request.user_id)

        return {
            "job_id": str(request.job_id),
            "message": "Automated analysis workflow completed successfully.",
            "eda_report": eda_report
        }
    except Exception as e:
        audit_service.log_event("wpa_auto_analysis_failed", request.job_id, request.user_id, status="failed", details={"error": str(e)})
        raise
