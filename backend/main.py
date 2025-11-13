from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
 
from pydantic import BaseModel
from typing import List, Dict, Any

from sqlalchemy import create_engine, text
from pymongo import MongoClient
from bson import ObjectId
import json
import boto3
 
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
    """Runs K-Means clustering analysis on the provided data."""
    task = run_kmeans_task.delay(data, k, features)
    return task.get(timeout=120)

@tool
def generate_correlation_heatmap(data: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generates a correlation heatmap for the numerical features in the data."""
    task = generate_correlation_heatmap_task.delay(data)
    return task.get(timeout=120)

@tool
def run_linear_regression(data: List[Dict[str, Any]], target: str, feature: str) -> Dict[str, Any]:
    """Runs a linear regression analysis with a specified target and feature."""
    task = run_linear_regression_task.delay(data, target, feature)
    return task.get(timeout=120)

@tool
def run_naive_bayes_classification(data: List[Dict[str, Any]], target: str, features: List[str]) -> Dict[str, Any]:
    """Runs Naive Bayes classification on the data with a specified target and features."""
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

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
 

class ChatRequest(BaseModel):
    message: str
    data: List[Dict[str, Any]]

 
class DbConnectionRequest(BaseModel):
    db_uri: str
    query: str

class MongoConnectionRequest(BaseModel):
    mongo_uri: str
    db_name: str
    collection_name: str

# Helper to serialize ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@app.post("/load-from-mongodb/")
async def load_from_mongodb(request: MongoConnectionRequest):
    try:
        client = MongoClient(request.mongo_uri)
        db = client[request.db_name]
        collection = db[request.collection_name]
        # We limit the results to avoid accidentally fetching millions of documents
        cursor = collection.find().limit(2000)
        docs = list(cursor)

        # Convert ObjectId to string for JSON serialization
        for doc in docs:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])

        df = pd.DataFrame(docs)
        df = df.where(pd.notna(df), None)
        return {"source": "mongodb", "data": df.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar o consultar MongoDB: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()

class S3ConnectionRequest(BaseModel):
    bucket_name: str
    object_key: str

async def process_uploaded_file_content(content: bytes, filename: str, sheet_name: str = None) -> (pd.DataFrame, List[str]):
    """Helper function to process file content into a DataFrame and return sheet names for Excel files."""
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    sheet_names = None
    try:
        if extension in ['csv', 'txt']:
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif extension in ['xlsx', 'xls']:
            # If a specific sheet is requested, load it. Otherwise, load the first one.
            if sheet_name:
                df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
                # We don't need to return all sheet names if one was already selected.
            else:
                df_dict = pd.read_excel(io.BytesIO(content), sheet_name=None)
                sheet_names = list(df_dict.keys())
                df = df_dict[sheet_names[0]] # Default to first sheet
        elif extension == 'json':
            df = pd.read_json(io.StringIO(content.decode('utf-8')))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: .{extension}")

        return df.where(pd.notna(df), None), sheet_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file content: {e}")

@app.post("/load-from-s3/")
async def load_from_s3(request: S3ConnectionRequest):
    try:
        # Boto3 will automatically look for credentials in standard locations:
        # 1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        # 2. IAM role for EC2/ECS/etc.
        s3_client = boto3.client('s3')

        response = s3_client.get_object(Bucket=request.bucket_name, Key=request.object_key)
        content = response['Body'].read()

        df, sheet_names = await process_uploaded_file_content(content, request.object_key)

        return {"source": "s3", "data": df.to_dict(orient='records'), "sheet_names": sheet_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading from S3: {e}")

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
async def upload_data(file: UploadFile = File(...), sheet_name: str = Query(None)):
    try:
        content = await file.read()
        df, sheet_names = await process_uploaded_file_content(content, file.filename, sheet_name)
        return {"filename": file.filename, "data": df.to_dict(orient='records'), "sheet_names": sheet_names}
    except Exception as e:
        # The HTTPException from the helper will be caught here
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error processing the uploaded file: {e}")

@app.post("/chat/agent/")
async def chat_agent_handler(request: ChatRequest):
    try:
        df = pd.DataFrame(request.data)
 
        data_preview = df.head().to_string() if not df.empty else "No hay datos cargados."
        response = await agent_executor.ainvoke({
            "input": request.message,
            "data_preview": data_preview,
            "data": request.data,
 
            "chat_history": []
        })
 
        return {"output": response.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el agente de IA: {e}")
