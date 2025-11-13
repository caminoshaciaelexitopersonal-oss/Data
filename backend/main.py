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
 
from langchain.agents import AgentExecutor
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
 
from langchain import hub
from prometheus_fastapi_instrumentator import Instrumentator

# --- Logger ---
from logger import log_step, get_logged_steps, clear_log

# --- Visualizations ---
from visualizations import add_visualization, get_all_visualizations, clear_visualizations

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
    # Log de código para SADI
    code = f"""
from sklearn.cluster import KMeans
import pandas as pd

df = pd.DataFrame(data)
X = df[{features}].values
kmeans = KMeans(n_clusters={k}, random_state=42, n_init=10)
kmeans.fit(X)
# ... post-processing ...
"""
    log_step(f"Ejecutando análisis K-Means con k={k} en las características: {features}", code)
    task = run_kmeans_task.delay(data, k, features)
    result = task.get(timeout=120)

    # Guardar datos para PVA
    if 'assignments' in result and 'centroids' in result:
        from collections import Counter
        counts = Counter(result['assignments'])
        colors = ["#22c55e", "#ef4444", "#3b82f6", "#f97316", "#8b5cf6"]
        cluster_data = [{"cluster": f"Grupo {i+1}", "count": counts[i], "color": colors[i % len(colors)]} for i in sorted(counts.keys())]
        add_visualization("kmeans_clusters", cluster_data)

    return result

@tool
def generate_correlation_heatmap(data: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generates a correlation heatmap for the numerical features in the data."""
    code = """
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame(data)
numeric_df = df.select_dtypes(include=['number'])
corr_matrix = numeric_df.corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
# ... guardar imagen a base64 ...
"""
    log_step("Generando mapa de calor de correlación", code)
    task = generate_correlation_heatmap_task.delay(data)
    return task.get(timeout=120)

@tool
def run_linear_regression(data: List[Dict[str, Any]], target: str, feature: str) -> Dict[str, Any]:
    """Runs a linear regression analysis with a specified target and feature."""
    code = f"""
import pandas as pd
from sklearn.linear_model import LinearRegression

df = pd.DataFrame(data)
X = df[['{feature}']].values
y = df['{target}].values
model = LinearRegression()
model.fit(X, y)
# ... calculando métricas ...
"""
    log_step(f"Ejecutando regresión lineal: target='{target}', feature='{feature}'", code)
    task = run_linear_regression_task.delay(data, target, feature)
    result = task.get(timeout=120)

    # Guardar datos para PVA
    if 'line_points' in result:
        df = pd.DataFrame(data)
        # Simplificamos para el ejemplo, tomando 100 puntos
        plot_data = [{"x": row[feature], "y_real": row[target], "y_pred": None} for _, row in df.sample(min(100, len(df))).iterrows()]
        # Añadimos la línea de regresión
        line_x = result['line_points']['x']
        line_y = result['line_points']['y']

        # Crear un modelo simple para predecir a lo largo de la trama
        model = LinearRegression()
        model.fit(df[[feature]], df[target])

        for i in range(len(plot_data)):
             plot_data[i]['y_pred'] = model.predict([[plot_data[i]['x']]])[0]

        add_visualization("regression_plot", plot_data)

    return result

@tool
def run_naive_bayes_classification(data: List[Dict[str, Any]], target: str, features: List[str]) -> Dict[str, Any]:
    """Runs Naive Bayes classification on the data with a specified target and features."""
    code = f"""
import pandas as pd
from sklearn.naive_bayes import GaussianNB

df = pd.DataFrame(data)
X = df[{features}].values
y = df['{target}].values
model = GaussianNB()
model.fit(X, y)
# ... calculando métricas ...
"""
    log_step(f"Ejecutando clasificación Naive Bayes: target='{target}', features={features}", code)
    task = run_naive_bayes_task.delay(data, target, features)
    result = task.get(timeout=120)

    # Guardar datos para PVA
    if 'accuracy' in result:
        add_visualization("classification_accuracy", [{"modelo": "Naive Bayes", "accuracy": result['accuracy']}])

    return result


tools = [run_kmeans_analysis, generate_correlation_heatmap, run_linear_regression, run_naive_bayes_classification]

# --- CONFIGURACIÓN DEL AGENTE PLAN-AND-EXECUTE ---
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
planner = load_chat_planner(llm)
executor = load_agent_executor(llm, tools, verbose=True)
agent_executor = PlanAndExecute(planner=planner, executor=executor, verbose=True)


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

@app.get("/get-steps")
def get_steps():
    """Endpoint para obtener los pasos y códigos ejecutados por el agente."""
    return {"steps": get_logged_steps()}

@app.get("/api/visualizations")
def get_visualizations():
    """Endpoint para obtener los datos de todas las visualizaciones generadas."""
    return get_all_visualizations()


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
        cursor = collection.find().limit(2000)
        docs = list(cursor)

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
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    sheet_names = None
    try:
        if extension in ['csv', 'txt']:
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif extension in ['xlsx', 'xls']:
            if sheet_name:
                df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
            else:
                df_dict = pd.read_excel(io.BytesIO(content), sheet_name=None)
                sheet_names = list(df_dict.keys())
                df = df_dict[sheet_names[0]]
        elif extension == 'json':
            df = pd.read_json(io.StringIO(content.decode('utf-8')))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: .{extension}")

        df_cleaned = df.where(pd.notna(df), None)

        # Generar datos para ETL summary en PVA
        if not df_cleaned.empty:
            numeric_cols = df_cleaned.select_dtypes(include=['number']).columns.tolist()
            summary = [{"feature": col, "mean": df_cleaned[col].mean(), "std": df_cleaned[col].std()} for col in numeric_cols]
            add_visualization("etl_summary", summary)

        return df_cleaned, sheet_names

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file content: {e}")

@app.post("/load-from-s3/")
async def load_from_s3(request: S3ConnectionRequest):
    try:
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

        df_cleaned = df.where(pd.notna(df), None)

        if not df_cleaned.empty:
            numeric_cols = df_cleaned.select_dtypes(include=['number']).columns.tolist()
            summary = [{"feature": col, "mean": df_cleaned[col].mean(), "std": df_cleaned[col].std()} for col in numeric_cols]
            add_visualization("etl_summary", summary)

        return {"source": "database", "data": df_cleaned.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar o consultar la base de datos: {e}")

 
@app.post("/upload-data/")
async def upload_data(file: UploadFile = File(...), sheet_name: str = Query(None)):
    try:
        content = await file.read()
        df, sheet_names = await process_uploaded_file_content(content, file.filename, sheet_name)
        return {"filename": file.filename, "data": df.to_dict(orient='records'), "sheet_names": sheet_names}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error processing the uploaded file: {e}")

@app.post("/chat/agent/")
async def chat_agent_handler(request: ChatRequest):
    try:
        clear_log()
        clear_visualizations()
        df = pd.DataFrame(request.data)
 
        data_preview = df.head().to_string() if not df.empty else "No hay datos cargados."

        inputs = {"input": request.message + "\n\nData Preview:\n" + data_preview}

        response = await agent_executor.ainvoke(inputs)
 
        return {"output": response.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el agente de IA: {e}")
