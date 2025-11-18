from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from backend.services.pipeline_selector import select_pipeline

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])

@router.post("/select")
async def get_pipeline_suggestion(metadata: Dict[str, Any] = Body(...)):
    """
    Recibe los metadatos del dataset y devuelve una sugerencia de pipeline de ETL.
    """
    if not metadata or 'dataset_shape' not in metadata:
        raise HTTPException(status_code=400, detail="Los metadatos del dataset son requeridos.")

    try:
        pipeline = select_pipeline(metadata)
        return {"suggested_pipeline": pipeline}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al seleccionar el pipeline: {e}")
