from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
import os

from backend.wpa.report_generation.schemas import ReportGenerationRequest, ReportGenerationResponse
from backend.wpa.report_generation.service import ReportGenerationService
from backend.audit.service import AuditService, audit_service

router = APIRouter(prefix="/wpa/reports", tags=["WPA - Report Generation"])

def get_report_generation_service():
    return ReportGenerationService()

@router.post("/generate", response_model=ReportGenerationResponse)
async def generate_report_endpoint(
    request: ReportGenerationRequest,
    report_service: ReportGenerationService = Depends(get_report_generation_service),
    audit: AuditService = Depends(lambda: audit_service)
):
    audit.log_event("wpa_report_generation_started", request.job_id)
    try:
        result = report_service.generate_report(request)
        file_path = result["file_path"]

        # In a real app, this would be a URL pointing to a static file server or cloud storage
        download_url = f"/wpa/reports/download/{os.path.basename(file_path)}"

        audit.log_event("wpa_report_generation_completed", request.job_id, details={"report_url": download_url})

        return ReportGenerationResponse(
            job_id=request.job_id,
            message="Report generated successfully.",
            report_url=download_url
        )
    except Exception as e:
        audit.log_event("wpa_report_generation_failed", request.job_id, status="failed", details={"error": str(e)})
        raise

@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Serves the generated report file for download.
    NOTE: This is a simplified approach for demonstration. In a production
    environment, files should be served via a dedicated static file server
    (like Nginx) or from a cloud storage service (like S3).
    """
    # This assumes the file is in the root directory, which is where generate_report saves it.
    file_path = f"./{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=filename)
    return {"error": "File not found."}
