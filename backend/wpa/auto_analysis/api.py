 
from fastapi import APIRouter, Depends, HTTPException
 
from pydantic import BaseModel
import pandas as pd
from typing import Dict, Any
import uuid
 
import mlflow
import hashlib

from backend.celery_worker import celery_app
from backend.app.services.state_store import StateStore, get_state_store
from backend.wpa.auto_analysis.ingestion_adapter import strengthen_ingestion
from backend.wpa.auto_analysis.eda_intelligent_service import run_eda
from backend.wpa.auto_analysis.model_trainer import train_and_select_model
# ... other imports

router = APIRouter(prefix="/wpa/auto-analysis", tags=["WPA - Automated Analysis"])
 
job_store: Dict[str, Dict[str, Any]] = {}

class SubmitRequest(BaseModel):
    session_id: str
 
    user_id: str = "default_user" # Example field

@celery_app.task(name="wpa.run_full_analysis_pipeline")
def run_full_analysis_pipeline_task(job_id: str, session_id: str, run_id: str):
    """Celery task for the analysis workflow."""
    state_store = get_state_store()
    try:
        with mlflow.start_run(run_id=run_id):
            job_store[job_id] = {"status": "running", "stage": "Loading Data"}
            df = state_store.load_dataframe(session_id)
            if df is None: raise ValueError("No data found for session ID.")

            mlflow.log_param("job_id", job_id)
            mlflow.log_param("session_id", session_id)

            job_store[job_id]["stage"] = "Strengthening Ingestion"
            metadata = strengthen_ingestion(df, job_id)

            job_store[job_id]["stage"] = "Running Automated EDA"
            run_eda(df, metadata['inferred_types'], job_id)

            # For brevity, subsequent steps are not shown but would log params/metrics
            # to MLflow within this 'with' block.

            job_store[job_id] = {"status": "completed", "stage": "Finished"}
    except Exception as e:
        mlflow.end_run(status="FAILED")
        job_store[job_id] = {"status": "failed", "stage": str(e)}

@router.post("/submit", status_code=202)
def submit_auto_analysis_job(request: SubmitRequest):
    """Submits a new analysis job and starts an MLflow run."""
    job_id = str(uuid.uuid4())

    # Create MLflow run
    experiment_name = "Automated Analysis"
    mlflow.set_experiment(experiment_name)
    run = mlflow.start_run()
    mlflow.set_tag("job_id", job_id)
    mlflow.set_tag("user_id", request.user_id)
    # Could also add git_commit tag here

    run_full_analysis_pipeline_task.delay(job_id, request.session_id, run.info.run_id)
    job_store[job_id] = {"status": "queued", "stage": "Awaiting worker", "mlflow_run_id": run.info.run_id}
    return {"job_id": job_id, "mlflow_run_id": run.info.run_id}

# Other endpoints remain the same
@router.get("/{job_id}/status")
def get_job_status(job_id: str):
    job = job_store.get(job_id)
    if not job: raise HTTPException(status_code=404, detail="Job not found.")
 
    return job

@router.get("/{job_id}/report")
def get_job_report(job_id: str):
 
    raise HTTPException(status_code=501, detail="Report retrieval not fully implemented in this phase.")
 
