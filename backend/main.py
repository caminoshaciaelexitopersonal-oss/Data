from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from typing import List
from fastapi.responses import FileResponse, StreamingResponse
import pandas as pd
from celery.result import AsyncResult
import io
import mlflow
import time
 
import os
 
 
from pydantic import BaseModel
from typing import List, Dict, Any

from sqlalchemy import create_engine, text
from pymongo import MongoClient
from bson import ObjectId
import json
import boto3
import base64
 
from langchain.agents import AgentExecutor
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.tools import tool
from langchain import hub
from prometheus_fastapi_instrumentator import Instrumentator

from backend.llm.llm_router import get_llm_for_agent
from audit_logger import log_data_ingestion

# --- Logger ---
from logger import log_step, get_logged_steps, clear_log

# --- Visualizations ---
from visualizations import add_visualization, get_all_visualizations, clear_visualizations

 
# --- Report Generator ---
from report_generator import generate_report, set_summary, clear_report_artifacts
from docx2pdf import convert

# --- Custom Services ---
from services import eda_service, pca_service
from app.export import code_exporter
 
from celery_worker import (
    run_kmeans_task,
    generate_correlation_heatmap_task,
    run_linear_regression_task,
    run_naive_bayes_task,
    train_random_forest_classifier_task,
    run_etl_pipeline_task,
    process_multiple_files_task,
    fetch_api_data_task
 
)

# --- Configuración de MLflow ---
mlflow.set_tracking_uri("http://mlflow:5000")

 
# (Todas las herramientas se mantienen igual)
 
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

@tool
def run_advanced_eda(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Ejecuta un Análisis Exploratorio de Datos (EDA) avanzado, generando estadísticas
    detalladas, histogramas y diagramas de caja para todas las variables numéricas.
    """
    code = "from services import eda_service\n\neda_results = eda_service.generate_advanced_eda(data)"
    log_step("Ejecutando Análisis Exploratorio de Datos (EDA) avanzado", code)

    eda_results = eda_service.generate_advanced_eda(data)

    if eda_results.get("status") == "success":
        # Podríamos añadir las estadísticas y gráficos al PVA si fuera necesario
        # Por ahora, solo devolvemos el resultado al agente.
        return eda_results
    else:
        return {"error": eda_results.get("message", "Error desconocido en el servicio EDA.")}

@tool
def run_pca_analysis(data: List[Dict[str, Any]], n_components: int = None) -> Dict[str, Any]:
    """
    Realiza un Análisis de Componentes Principales (PCA) para reducir la dimensionalidad.

    :param data: La lista de datos a analizar.
    :param n_components: El número de componentes principales a retener. Si no se especifica,
                         se calcularán todos los componentes posibles.
    """
    code = f"from services import pca_service\n\npca_results = pca_service.perform_pca_analysis(data, n_components={n_components})"
    log_step(f"Ejecutando Análisis de Componentes Principales (PCA) con {n_components or 'todos los'} componentes", code)

    pca_results = pca_service.perform_pca_analysis(data, n_components)

    if pca_results.get("status") == "success":
        # Registrar el experimento en MLflow
        mlflow.set_experiment("SADI_Dimensionality_Reduction")
        with mlflow.start_run() as run:
            mlflow.log_param("model", "PCA")
            mlflow.log_param("n_components", n_components or 'all')
            mlflow.log_metric("explained_variance_ratio_pc1", pca_results["explained_variance_ratio"][0])

            # Guardar el gráfico de varianza explicada como un artefacto
            plot_base64 = pca_results["plots"]["explained_variance_plot"]
            plot_bytes = base64.b64decode(plot_base64)
            plot_path = f"/tmp/{run.info.run_id}_explained_variance.png"
            with open(plot_path, "wb") as f:
                f.write(plot_bytes)
            mlflow.log_artifact(plot_path, "plots")

        # Enviar datos y gráficos al PVA y al generador de informes
        add_visualization("pca_explained_variance", {
            "components": list(range(1, len(pca_results["cumulative_explained_variance"]) + 1)),
            "cumulative_variance": pca_results["cumulative_explained_variance"]
        })
        # from report_generator import add_plot # (Asegurarse de que esté importado arriba)
        # add_plot("pca_explained_variance", io.BytesIO(plot_bytes))

        return pca_results
    else:
        return {"error": pca_results.get("message", "Error desconocido en el servicio PCA.")}

 
tools = [
    fetch_api_data,
    execute_etl_pipeline,
    run_kmeans_analysis,
    generate_correlation_heatmap,
    run_linear_regression,
    run_naive_bayes_classification,
    train_random_forest_classifier,
    run_advanced_eda,
    run_pca_analysis
]

# --- APP FASTAPI y Configuración del Agente ---
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)


# --- Configuración del Agente y LLM ---
# Esta sección se reconfigurará dinámicamente por solicitud en el endpoint del agente.

 
# --- Endpoints ---
@app.get("/download-report")
def download_report(format: str = Query("docx", enum=["docx", "pdf"])):
    """
    Genera y devuelve el informe analítico en formato .docx o .pdf.
    """
    try:
        report_buffer = generate_report()
        temp_docx_path = "/tmp/sadi_report.docx"

        with open(temp_docx_path, "wb") as f:
            f.write(report_buffer.read())

        if format == "pdf":
            temp_pdf_path = "/tmp/sadi_report.pdf"

            # Verificar si el archivo PDF ya existe y eliminarlo para evitar errores de sobreescritura
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

            convert(temp_docx_path, temp_pdf_path)

            return FileResponse(
                path=temp_pdf_path,
                media_type='application/pdf',
                filename='SADI_Informe_Analitico.pdf'
            )
        else: # format == "docx"
            return FileResponse(
                path=temp_docx_path,
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                filename='SADI_Informe_Analitico.docx'
            )
    except Exception as e:
        # Considerar un logging más robusto en producción
        print(f"ERROR generating report: {e}")
        raise HTTPException(status_code=500, detail=f"No se pudo generar el informe: {e}")

@app.post("/chat/agent/")
async def chat_agent_handler(request: ChatRequest):
    try:
        # Limpiar artefactos de ejecuciones anteriores
        clear_log()
        clear_visualizations()
        clear_report_artifacts()

        df = pd.DataFrame(request.data)
        data_preview = df.head().to_string() if not df.empty else "No hay datos cargados."
        prompt = request.message + "\n\nData Preview:\n" + data_preview
        inputs = {"input": prompt}

        # --- Reconfiguración dinámica del Agente por solicitud ---
        llm = get_llm_for_agent(model_preference=request.llm_preference)
        planner = load_chat_planner(llm)
        executor = load_agent_executor(llm, tools, verbose=True)
        agent_executor = PlanAndExecute(planner=planner, executor=executor, verbose=True)
        # --- Fin de la reconfiguración ---

        start_time = time.time()

        # Ejecutar el agente
        response = await agent_executor.ainvoke(inputs)

        end_time = time.time()
        execution_time_ms = (end_time - start_time) * 1000

        # Guardar la salida del agente como el resumen del informe
        output = response.get("output", "El agente no produjo una conclusión final.")
        set_summary(output)

        # Log avanzado
        log_step(
            description="Ejecución completa del agente Plan-and-Execute",
            code_snippet=f"agent_executor.ainvoke(message='{request.message}')",
            llm_prompt=prompt,
            llm_response=output,
            execution_time_ms=execution_time_ms
        )

        return {"output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el agente de IA: {e}")


# (El resto de la aplicación se mantiene igual)
# ...
 
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

@app.get("/audit-log")
def get_audit_log():
    """Endpoint para obtener el log de auditoría completo."""
    log_file_path = os.path.join('data', 'logs', 'audit_log.json')
    try:
        if not os.path.exists(log_file_path):
            return []  # Devuelve una lista vacía si el log aún no existe

        with open(log_file_path, 'r') as f:
            logs = json.load(f)

        # Ordenar logs por timestamp descendente (los más recientes primero)
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return logs
    except (IOError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el log de auditoría: {e}")


from typing import Optional

class ChatRequest(BaseModel):
    message: str
    data: List[Dict[str, Any]]
    llm_preference: Optional[str] = None

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

        # Log the data ingestion event
        if not df.empty:
            log_data_ingestion(
                source_type="mongodb",
                source_identifier=f"mongodb://.../{request.db_name}/{request.collection_name}",
                user_or_agent="user_mongodb_connection",
                data=df
            )

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

            # Log the data ingestion event for auditing
            log_data_ingestion(
                source_type="file_upload",
                source_identifier=filename,
                user_or_agent="user_upload", # This could be enhanced with user auth
                data=df_cleaned
            )

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

            # Log the data ingestion event
            log_data_ingestion(
                source_type="database",
                source_identifier=f"db_{request.db_uri.split('@')[-1]}", # Anonymize credentials
                user_or_agent="user_db_connection",
                data=df_cleaned
            )

        return {"source": "database", "data": df_cleaned.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar o consultar la base de datos: {e}")

 
@app.post("/upload/multi", status_code=202)
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Endpoint para cargar y procesar múltiples archivos de datos de forma asíncrona.
    """
    try:
        file_contents = {file.filename: await file.read() for file in files}

        # Pasar el contenido de los archivos a una tarea de Celery
        task = process_multiple_files_task.delay(file_contents)

        return {"task_id": task.id, "message": "Los archivos han sido recibidos y están siendo procesados."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar el procesamiento de archivos: {e}")

@app.get("/api/v1/etl/status/{task_id}")
def get_etl_job_status(task_id: str):
    """
    Consulta el estado de un trabajo ETL previamente iniciado.
    """
    task_result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else "Pending or running..."
    }

    if task_result.failed():
        response["result"] = str(task_result.info) # Muestra la excepción

    return response

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

@app.get("/export/code")
def export_code():
    """
    Exporta todos los pasos de código generados por el agente en un archivo .zip.
    """
    try:
        steps = get_logged_steps()
        if not steps:
            raise HTTPException(status_code=404, detail="No se ha generado ningún código para exportar.")

        zip_buffer = code_exporter.export_code_blocks_to_zip(steps)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=sadi_codigo_exportado.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar el código: {e}")
