from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from sqlalchemy import create_engine, text
import os

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub # Importar hub

from tools import run_kmeans_tool, generate_correlation_heatmap_tool, run_linear_regression_tool

# --- HERRAMIENTAS DEL AGENTE ---
@tool
def run_kmeans_analysis(data: List[Dict[str, Any]], k: int, features: List[str]) -> Dict[str, Any]:
    """
    Ejecuta el algoritmo K-Means. Úsalo cuando el usuario pida agrupar o segmentar sus datos.
    Debes preguntarle al usuario el número de clusters (k) y las características (features) a usar si no te las ha proporcionado.
    """
    return run_kmeans_tool(data, k, features)

@tool
def generate_correlation_heatmap(data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Genera un mapa de calor de correlación para las características numéricas.
    Úsalo cuando el usuario pida 'explorar', 'analizar relaciones', o 'ver correlaciones'.
    """
    return generate_correlation_heatmap_tool(data)

@tool
def run_linear_regression(data: List[Dict[str, Any]], target: str, feature: str) -> Dict[str, Any]:
    """
    Realiza un análisis de regresión lineal simple para predecir una variable objetivo.
    Úsalo cuando el usuario quiera predecir un valor o entender la relación lineal entre dos variables.
    """
    return run_linear_regression_tool(data, target, feature)


tools = [run_kmeans_analysis, generate_correlation_heatmap, run_linear_regression]

# --- CONFIGURACIÓN DEL AGENTE ---
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

# Descargar un prompt de agente ReAct probado desde LangChain Hub
agent_prompt = hub.pull("hwchase17/react-chat")

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ----------------------------------------

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

class ChatRequest(BaseModel):
    message: str
    data: List[Dict[str, Any]]

@app.post("/upload-data/")
async def upload_data(file: UploadFile = File(...)):
    filename = file.filename
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    try:
        content = await file.read()
        if extension in ['csv', 'txt']:
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif extension in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(content), sheet_name=None)
            if isinstance(df, dict):
                first_sheet = next(iter(df.values()))
                first_sheet = first_sheet.where(pd.notna(first_sheet), None)
                return {"filename": filename, "data": first_sheet.to_dict(orient='records'), "sheets": list(df.keys())}
        elif extension == 'json':
            df = pd.read_json(io.StringIO(content.decode('utf-8')))
        else:
            raise HTTPException(status_code=400, detail=f"Tipo de archivo no soportado: .{extension}")

        df = df.where(pd.notna(df), None)
        return {"filename": filename, "data": df.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")

@app.post("/chat/agent/")
async def chat_agent_handler(request: ChatRequest):
    try:
        df = pd.DataFrame(request.data)
        if not df.empty:
            data_preview = df.head().to_string()
        else:
            data_preview = "No hay datos cargados."

        # El prompt de hub necesita una variable "chat_history"
        response = await agent_executor.ainvoke({
            "input": request.message,
            "data_preview": data_preview,
            "data": request.data,
            "chat_history": [] # Pasar un historial de chat vacío por ahora
        })

        return {"output": response.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el agente de IA: {e}")
