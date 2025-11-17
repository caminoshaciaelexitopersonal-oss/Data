from fastapi import APIRouter, Depends
import pandas as pd # Import pandas here

from backend.wpa.modeling.schemas import (
    ModelTrainRequest, ModelTrainResponse,
    ModelPredictRequest, ModelPredictResponse
)
from backend.wpa.modeling.service import ModelingService
from backend.audit.service import AuditService, audit_service
from backend.wpa.session_manager import session_manager

router = APIRouter(prefix="/wpa/modeling", tags=["WPA - Modeling"])

def get_modeling_service():
    return ModelingService(session_manager=session_manager)

@router.post("/train", response_model=ModelTrainResponse)
async def train_model(
    request: ModelTrainRequest,
    modeling_service: ModelingService = Depends(get_modeling_service),
    audit: AuditService = Depends(lambda: audit_service)
):
    audit.log_event("wpa_modeling_train_started", request.job_id)
    try:
        result = modeling_service.train_model(request)
        audit.log_event("wpa_modeling_train_completed", request.job_id, details=result)
        return ModelTrainResponse(
            job_id=request.job_id,
            message="Model training completed successfully.",
            **result
        )
    except Exception as e:
        audit.log_event("wpa_modeling_train_failed", request.job_id, status="failed", details={"error": str(e)})
        raise

@router.post("/predict", response_model=ModelPredictResponse)
async def predict(
    request: ModelPredictRequest,
    modeling_service: ModelingService = Depends(get_modeling_service),
    audit: AuditService = Depends(lambda: audit_service)
):
    audit.log_event("wpa_modeling_predict_started", request.job_id)
    try:
        predictions = modeling_service.predict(request.mlflow_run_id, request.prediction_data)
        audit.log_event("wpa_modeling_predict_completed", request.job_id)
        return ModelPredictResponse(
            job_id=request.job_id,
            message="Prediction completed successfully.",
            predictions=predictions
        )
    except Exception as e:
        audit.log_event("wpa_modeling_predict_failed", request.job_id, status="failed", details={"error": str(e)})
        raise
