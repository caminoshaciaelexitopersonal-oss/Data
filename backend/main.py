from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import mlflow
 
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
    run_naive_bayes_task,
    train_random_forest_classifier_task,
    run_etl_pipeline_task,
    fetch_api_data_task # Importar nueva tarea
)

# --- Configuración de MLflow ---
mlflow.set_tracking_uri("http://mlflow:5000")

# --- HERRAMIENTAS DEL AGENTE ---
@tool
def fetch_api_data(url: str) -> Dict[str, Any]:
    """
    Obtiene datos desde una URL de API externa. La URL debe devolver una respuesta JSON
    que sea una lista de objetos.
    """
    code = f"import httpx\n\nresponse = httpx.get('{url}')\ndata = response.json()"
    log_step(f"Obteniendo datos desde la API: {url}", code)

    task = fetch_api_data_task.delay(url)
    api_data = task.get(timeout=120)

    # Procesar los datos para el PVA (igual que en la carga de archivos)
    if api_data:
        df = pd.DataFrame(api_data)
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        summary = [{"feature": col, "mean": df[col].mean(), "std": df[col].std()} for col in numeric_cols]
        add_visualization("etl_summary", summary)

    return {
        "message": f"Datos obtenidos con éxito desde {url}. Se encontraron {len(api_data)} registros.",
        "data": api_data
    }


@tool
def execute_etl_pipeline(data: List[Dict[str, Any]], pipeline_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Ejecuta un pipeline de limpieza y transformación de datos (ETL).
    'pipeline_steps' debe ser una lista de diccionarios, donde cada diccionario define una acción.
    Ejemplo: [{"action": "drop_nulls", "column": "nombre_columna"}]
    Devuelve los datos transformados.
    """
    code = f"pipeline = {json.dumps(pipeline_steps, indent=2)}\n# ... código de ejecución del pipeline ..."
    log_step(f"Ejecutando pipeline ETL de {len(pipeline_steps)} pasos", code)

    task = run_etl_pipeline_task.delay(data, pipeline_steps)
    transformed_data = task.get(timeout=300)

    return {
        "message": f"Pipeline ETL ejecutado con éxito. Se procesaron {len(transformed_data)} filas.",
        "processed_data": transformed_data
    }

@tool
def train_random_forest_classifier(data: List[Dict[str, Any]], target: str, features: List[str]) -> Dict[str, Any]:
    """
    Entrena un modelo de clasificación RandomForest sobre los datos proporcionados,
    registra el experimento en MLflow y devuelve el ID de la ejecución y la precisión.
    """
    experiment_name = "SADI_Classification"
    code = f"""
import mlflow
from sklearn.ensemble import RandomForestClassifier

mlflow.set_experiment("{experiment_name}")
with mlflow.start_run():
    # ... código de entrenamiento ...
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    mlflow.sklearn.log_model(model, "random_forest_model")
"""
    log_step(f"Entrenando RandomForest para predecir '{target}' usando {features}", code)
    task = train_random_forest_classifier_task.delay(data, target, features, experiment_name)
    result = task.get(timeout=300)

    if 'accuracy' in result:
        current_data = get_all_visualizations().get("classification_accuracy", [])
        current_data.append({"modelo": "Random Forest", "accuracy": result['accuracy']})
        add_visualization("classification_accuracy", current_data)

    return result

# (Resto de herramientas se mantienen igual)
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


tools = [
    fetch_api_data, # Nueva herramienta
    execute_etl_pipeline,
    run_kmeans_analysis,
    generate_correlation_heatmap,
    run_linear_regression,
    run_naive_bayes_classification,
    train_random_forest_classifier
]

# (Configuración del agente y de la app FastAPI se mantiene igual)

# --- APP FASTAPI ---
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)

# --- CONFIGURACIÓN DEL AGENTE PLAN-AND-EXECUTE ---
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
planner = load_chat_planner(llm)
executor = load_agent_executor(llm, tools, verbose=True)
agent_executor = PlanAndExecute(planner=planner, executor=executor, verbose=True)



# (Endpoints existentes se mantienen igual)
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

class PredictionRequest(BaseModel):
    run_id: str
    data: List[Dict[str, Any]]

class PipelineRequest(BaseModel):
    data: List[Dict[str, Any]]
    steps: List[Dict[str, Any]]

@app.post("/predict/")
async def predict(request: PredictionRequest):
    """Carga un modelo desde MLflow y realiza predicciones."""
    try:
        # Cargar el modelo usando el run_id
        logged_model = f"runs:/{request.run_id}/random_forest_model"
        loaded_model = mlflow.sklearn.load_model(logged_model)

        # Preparar datos para la predicción
        df_to_predict = pd.DataFrame(request.data)

        predictions = loaded_model.predict(df_to_predict)

        return {"predictions": predictions.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la predicción: {e}")

@app.post("/run-pipeline/")
async def run_pipeline_endpoint(request: PipelineRequest):
    """Endpoint para ejecutar un pipeline ETL directamente."""
    try:
        task = run_etl_pipeline_task.delay(request.data, request.steps)
        transformed_data = task.get(timeout=300)
        return {"processed_data": transformed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando el pipeline: {e}")

# (Resto de los endpoints de carga de datos se mantienen igual)
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
