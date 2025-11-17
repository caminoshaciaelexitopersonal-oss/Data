from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import zipfile
import io

from backend.logger import get_logged_steps, log_step
from backend.visualizations import get_all_visualizations
from backend.report_generator import generate_report
from backend.schemas import ChatRequest
from fastapi import Request

router = APIRouter()

def get_agent_executor(request: Request):
    return request.app.state.agent_executor

@router.get("/get-steps")
async def get_steps():
    return {"steps": get_logged_steps()}

@router.get("/visualizations")
async def visualizations():
    return get_all_visualizations()

@router.get("/download-report")
async def download_report():
    try:
        file_path = generate_report()
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=os.path.basename(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {e}")

import time
from uuid import uuid4
from backend.services.prompt_tracer import PromptTracerService, get_prompt_tracer_service

@router.post("/chat/agent/")
async def chat_agent(
    request: ChatRequest,
    agent_executor = Depends(get_agent_executor),
    tracer_service: PromptTracerService = Depends(get_prompt_tracer_service)
):
    try:
        # Assume a session_id is passed in the request, or generate one.
        session_id = str(getattr(request, 'session_id', uuid4()))
        start_time = time.time()

        result = await agent_executor.ainvoke({"input": request.message, "data": request.data})

        end_time = time.time()
        execution_time = end_time - start_time

        # Determine model used (this might need to be sourced from the agent's config)
        model_used = "default_model"

        tracer_service.log_prompt(
            session_id=session_id,
            prompt=request.message,
            response=result,
            model_used=model_used,
            execution_time=execution_time
        )

        # Manejo robusto:
        if isinstance(result, dict) and "output" in result:
            return {"output": result["output"]}
        # fallback defensivo
        return {"output": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el agente de chat: {e}")

@router.get("/export/code")
async def export_code():
    """
    Exports the logged code steps into a structured ZIP file.
    """
    steps = get_logged_steps()
    if not steps:
        raise HTTPException(status_code=404, detail="No hay pasos de código para exportar.")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Create a main script file
        main_script_content = "# Script principal generado por SADI\n\n"
        for i, step in enumerate(steps):
            step_filename = f"step_{i+1}_{step['description'].replace(' ', '_').lower()}.py"
            zip_file.writestr(f"steps/{step_filename}", step['code'])
            main_script_content += f"print('--- Ejecutando paso: {step['description']} ---')\n"
            main_script_content += f"exec(open('steps/{step_filename}').read())\n\n"

        zip_file.writestr("main.py", main_script_content)

    zip_buffer.seek(0)
    return FileResponse(zip_buffer, media_type='application/zip', filename="sadi_exported_code.zip")
