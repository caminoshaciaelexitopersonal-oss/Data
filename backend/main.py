from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
 
from pydantic import BaseModel
from typing import List, Dict, Any

from sqlalchemy import create_engine, text
 
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
 
from langchain import hub
from prometheus_fastapi_instrumentator import Instrumentator

from celery_worker import (
    run_kmeans_task,
    generate_correlation_heatmap_task,
    run_linear_regression_task,
    run_naive_bayes_task
)

# --- HERRAMIENTAS DEL AGENTE (DESPACHAN TAREAS) ---
@tool
def run_kmeans_analysis(data: List[Dict[str, Any]], k: int, features: List[str]) -> Dict[str, Any]:
    task = run_kmeans_task.delay(data, k, features)
    return task.get(timeout=120)

@tool
def generate_correlation_heatmap(data: List[Dict[str, Any]]) -> Dict[str, str]:
    task = generate_correlation_heatmap_task.delay(data)
    return task.get(timeout=120)

@tool
def run_linear_regression(data: List[Dict[str, Any]], target: str, feature: str) -> Dict[str, Any]:
    task = run_linear_regression_task.delay(data, target, feature)
    return task.get(timeout=120)

@tool
def run_naive_bayes_classification(data: List[Dict[str, Any]], target: str, features: List[str]) -> Dict[str, Any]:
    task = run_naive_bayes_task.delay(data, target, features)
    return task.get(timeout=120)

tools = [run_kmeans_analysis, generate_correlation_heatmap, run_linear_regression, run_naive_bayes_classification]

# --- CONFIGURACIÓN DEL AGENTE ---
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
agent_prompt = hub.pull("hwchase17/react-chat")
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- APP FASTAPI ---
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)
 

class ChatRequest(BaseModel):
    message: str
    data: List[Dict[str, Any]]

 
class DbConnectionRequest(BaseModel):
    db_uri: str
    query: str

@app.post("/load-from-db/")
async def load_from_db(request: DbConnectionRequest):
    try:
        engine = create_engine(request.db_uri)
        with engine.connect() as connection:
            df = pd.read_sql(text(request.query), connection)
        df = df.where(pd.notna(df), None)
        return {"source": "database", "data": df.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar o consultar la base de datos: {e}")

 
@app.post("/upload-data/")
async def upload_data(file: UploadFile = File(...)):
    filename = file.filename
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    try:
        content = await file.read()
        if extension in ['csv', 'txt']:
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif extension in ['xlsx', 'xls']:
 
            df_dict = pd.read_excel(io.BytesIO(content), sheet_name=None)
            sheet_names = list(df_dict.keys())
            df = df_dict[sheet_names[0]]
 
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
 
        data_preview = df.head().to_string() if not df.empty else "No hay datos cargados."
 main
        response = await agent_executor.ainvoke({
            "input": request.message,
            "data_preview": data_preview,
            "data": request.data,
 
            "chat_history": []
        })
 
        return {"output": response.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el agente de IA: {e}")
