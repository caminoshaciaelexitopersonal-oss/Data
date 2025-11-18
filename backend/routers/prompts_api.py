import os
import json
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

LOG_DIR = "data/logs/prompts"

router = APIRouter(prefix="/prompts", tags=["Prompts"])

@router.get("/trace/{session_id}", response_model=List[Dict[str, Any]])
async def get_prompt_traces(session_id: str):
    """
    Recupera todas las trazas de prompts para una sesión específica.
    """
    traces = []
    if not os.path.exists(LOG_DIR):
        return traces

    for filename in sorted(os.listdir(LOG_DIR)):
        if filename.startswith(session_id) and filename.endswith(".json"):
            file_path = os.path.join(LOG_DIR, filename)
            try:
                with open(file_path, "r") as f:
                    traces.append(json.load(f))
            except Exception as e:
                # Omitir archivos corruptos, pero registrar el error
                print(f"Error al leer el archivo de traza {filename}: {e}")

    if not traces:
        raise HTTPException(status_code=404, detail="No se encontraron trazas para la sesión especificada.")

    return traces
