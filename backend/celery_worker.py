from celery import Celery
from tools import run_kmeans_tool, generate_correlation_heatmap_tool, run_linear_regression_tool, run_naive_bayes_tool
from typing import List, Dict, Any
import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from pipeline import run_pipeline as execute_etl_pipeline
import httpx # Importar httpx

# Configura Celery. Usa Redis como broker.
celery_app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')
mlflow.set_tracking_uri("http://mlflow:5000")

# --- Tarea para Fetch de API ---
@celery_app.task
def fetch_api_data_task(url: str) -> List[Dict[str, Any]]:
    """Tarea de Celery para obtener datos de una API externa."""
    try:
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True)
            response.raise_for_status() # Lanza excepción para códigos de error HTTP

            # Asumimos que la respuesta es un JSON con una lista de objetos
            return response.json()
    except httpx.RequestError as e:
        # Manejar errores de red
        raise Exception(f"Error de red al acceder a la API: {e}")
    except Exception as e:
        # Manejar otros errores (JSON inválido, etc.)
        raise Exception(f"Error al procesar la respuesta de la API: {e}")


# --- Tareas de Machine Learning ---
@celery_app.task
def run_kmeans_task(data: List[Dict[str, Any]], k: int, features: List[str]) -> Dict[str, Any]:
    return run_kmeans_tool(data, k, features)

@celery_app.task
def generate_correlation_heatmap_task(data: List[Dict[str, Any]]) -> Dict[str, str]:
    return generate_correlation_heatmap_tool(data)

@celery_app.task
def run_linear_regression_task(data: List[Dict[str, Any]], target: str, feature: str) -> Dict[str, Any]:
    return run_linear_regression_tool(data, target, feature)

@celery_app.task
def run_naive_bayes_task(data: List[Dict[str, Any]], target: str, features: List[str]) -> Dict[str, Any]:
    return run_naive_bayes_tool(data, target, features)

@celery_app.task
def train_random_forest_classifier_task(
    data: List[Dict[str, Any]], target: str, features: List[str], experiment_name: str
) -> Dict[str, Any]:
    """Entrena un RandomForestClassifier y lo registra en MLflow."""
    df = pd.DataFrame(data)

    mlflow.set_experiment(experiment_name)
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        X = df[features]
        y = df[target]

        n_estimators = 100
        max_depth = 10

        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(model, "random_forest_model")

        return {
            "message": "Modelo entrenado y registrado en MLflow con éxito.",
            "run_id": run_id,
            "accuracy": accuracy
        }

# --- Tarea de Pipeline ETL ---
@celery_app.task
def run_etl_pipeline_task(data: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ejecuta un pipeline ETL sobre los datos.
    """
    df = pd.DataFrame(data)
    transformed_df = execute_etl_pipeline(df, steps)
    return transformed_df.to_dict(orient='records')

# --- Nueva Tarea ETL Multi-Fuente ---
from backend.app.services.etl_multisource_service import run_full_etl_process

@celery_app.task(name='celery_worker.process_multiple_files_task')
def process_multiple_files_task(file_contents: Dict[str, bytes]) -> Dict[str, Any]:
    """
    Tarea de Celery para orquestar el procesamiento ETL de múltiples archivos cargados.
    """
    try:
        result = run_full_etl_process(file_contents)
        return {
            "status": "SUCCESS",
            "message": "Procesamiento ETL completado.",
            "results": result
        }
    except Exception as e:
        # En caso de error, el estado de la tarea se marcará como FAILURE
        # y la excepción se almacenará en el resultado de la tarea.
        # Aquí se re-lanza para que Celery lo maneje.
        raise e
