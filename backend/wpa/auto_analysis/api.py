from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pandas as pd
from typing import Dict, Any
import uuid

from backend.app.services.state_store import StateStore, get_state_store
from backend.wpa.auto_analysis.ingestion_adapter import strengthen_ingestion
from backend.wpa.auto_analysis.eda_intelligent_service import run_eda
from backend.wpa.auto_analysis.stats_engine import StatsEngine
from backend.wpa.auto_analysis.target_detector import detect_target_variable
from backend.wpa.auto_analysis.model_trainer import train_and_select_model
from backend.wpa.auto_analysis.explainability_engine import generate_model_explanations
from backend.wpa.auto_analysis.report_generator import generate_report

router = APIRouter(prefix="/wpa/auto-analysis", tags=["WPA - Automated Analysis"])

# --- In-memory store for job status and results ---
# In a real-world scenario, this would be a persistent store like Redis or a database.
job_store: Dict[str, Dict[str, Any]] = {}

class SubmitRequest(BaseModel):
    session_id: str

def run_full_analysis_pipeline(job_id: str, session_id: str, state_store: StateStore):
    """
    The main function that orchestrates the entire automated analysis workflow.
    """
    try:
        job_store[job_id] = {"status": "running", "stage": "Loading Data", "result": None}

        # 1. Load Data from StateStore
        df = state_store.load_dataframe(session_id)
        if df is None:
            raise ValueError("No data found for the given session ID.")

        # 2. Ingestion Strengthening
        job_store[job_id]["stage"] = "Strengthening Ingestion"
        metadata = strengthen_ingestion(df)

        # 3. Automated EDA
        job_store[job_id]["stage"] = "Running Automated EDA"
        eda_report = run_eda(df, metadata['inferred_types'])

        # 4. Target Detection
        job_store[job_id]["stage"] = "Detecting Target Variable"
        target_detection = detect_target_variable(df, metadata)
        target = target_detection['detected_target']
        if not target:
            raise ValueError("Could not automatically detect a target variable.")

        # 5. Model Training
        job_store[job_id]["stage"] = "Training and Evaluating Models"
        model_results = train_and_select_model(df, target, eda_report['variable_classification'])

        # 6. Explainability
        job_store[job_id]["stage"] = "Generating Model Explanations"
        explanations = generate_model_explanations(
            model_results['trained_pipeline'],
            df.drop(columns=[target]),
            df[target]
        )

        # 7. Report Generation
        job_store[job_id]["stage"] = "Generating Final Report"
        analysis_summary = {
            "metadata": metadata,
            "eda_report": eda_report,
            "target_detection": target_detection,
            "model_results": {k: v for k, v in model_results.items() if k != 'trained_pipeline'}, # Exclude pipeline object
            "explanations": explanations
        }
        html_report = generate_report(job_id, analysis_summary)

        job_store[job_id] = {"status": "completed", "stage": "Finished", "result": html_report}

    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        job_store[job_id] = {"status": "failed", "stage": str(e), "result": None}


@router.post("/submit", status_code=202)
def submit_auto_analysis_job(
    request: SubmitRequest,
    background_tasks: BackgroundTasks,
    state_store: StateStore = Depends(get_state_store)
):
    """
    Submits a new automated analysis job to run in the background.
    """
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_full_analysis_pipeline, job_id, request.session_id, state_store)
    return {"job_id": job_id, "message": "Automated analysis job started."}

@router.get("/{job_id}/status")
def get_job_status(job_id: str):
    """
    Retrieves the current status of an analysis job.
    """
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

@router.get("/{job_id}/report")
def get_job_report(job_id: str):
    """
    Retrieves the final HTML report for a completed job.
    """
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job is not complete. Current status: {job['status']}")

    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=job["result"], status_code=200)
