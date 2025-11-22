from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
import os
import zipfile
import io
import uuid

from backend.logger import get_logged_steps, log_step
from backend.visualizations import get_all_visualizations
from backend.report_generator import generate_report
import pandas as pd
from backend.agent.pre_analysis import detect_intent
from backend.schemas import ChatRequest
from fastapi import Request
from backend.services.prompt_tracer import PromptTracerService, get_prompt_tracer_service

router = APIRouter()

def get_agent_executor(request: Request):
    return request.app.state.agent_executor

@router.get("/get-steps")
async def get_steps(session_id: str = Query(...)):
    return {"steps": get_logged_steps(session_id=session_id)}

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

@router.post("/chat/agent/")
async def chat_agent(
    request: ChatRequest,
    agent_executor = Depends(get_agent_executor),
    tracer_service: PromptTracerService = Depends(get_prompt_tracer_service)
):
    if agent_executor is None:
        raise HTTPException(
            status_code=503,
            detail="El agente de IA no está disponible. Verifique la configuración de la clave API del LLM."
        )

    session_id = request.session_id or str(uuid.uuid4())
    try:
        # 1. Crear un DataFrame de muestra para el pre-análisis
        df_sample = pd.DataFrame(request.data)

        # 2. Ejecutar el pre-análisis inteligente
        analysis = detect_intent(request.message, df_sample)

        # 3. Enriquecer el input del agente con el contexto del pre-análisis
        enriched_input = (
            f"User Query: \"{request.message}\"\n"
            f"Pre-analysis Intent: {analysis['intent']}\n"
            f"Dataset Context: {analysis['context']}"
        )

        # 4. Invocar al agente con el input enriquecido
        result = await agent_executor.ainvoke({
            "input": enriched_input,
            "data": request.data,
            "config": {"configurable": {"session_id": session_id}}
        })
  
        # Manejo robusto:
        if isinstance(result, dict) and "output" in result:
            return {"output": result["output"]}
        # fallback defensivo
        return {"output": str(result)}
    except Exception as e:
        tracer_service.log_prompt(
            session_id=session_id,
            prompt=request.message,
            response={"error": str(e)},
            model_used="error_handler",
            execution_time=0.0
        )
        raise HTTPException(status_code=500, detail=f"Error en el agente de chat: {e}")

@router.get("/export/code")
async def export_code(session_id: str = Query(...)):
    """
    Exports the logged code steps into a structured ZIP file.
    """
    steps = get_logged_steps(session_id=session_id)
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
