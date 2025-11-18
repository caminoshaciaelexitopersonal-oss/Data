from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import os

from backend.services.environment_exporter import EnvironmentExporterService, get_environment_exporter_service
from pydantic import BaseModel

router = APIRouter(prefix="/export", tags=["Export"])

class ExportRequest(BaseModel):
    job_id: str
    mlflow_run_id: str = None

@router.post("/environment", response_class=FileResponse)
async def export_environment(
    request: ExportRequest,
    exporter_service: EnvironmentExporterService = Depends(get_environment_exporter_service)
):
    """
    Exports all environment artifacts for a given job_id.
    """
    try:
        zip_path = exporter_service.export_full_environment(request.job_id, request.mlflow_run_id)
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=404, detail="Export file not found after generation.")

        return FileResponse(
            path=zip_path,
            filename=os.path.basename(zip_path),
            media_type='application/zip'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export environment: {e}")
