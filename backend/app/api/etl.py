from fastapi import APIRouter, HTTPException
from backend.schemas import PipelineRequest
from backend.services.etl_service import process_pipeline
import pandas as pd

router = APIRouter()

@router.post("/run-pipeline/")
async def run_pipeline(request: PipelineRequest):
    try:
        df = pd.DataFrame(request.data)
        processed_df = process_pipeline(df, request.steps)
        return {"processed_data": processed_df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el pipeline: {e}")
