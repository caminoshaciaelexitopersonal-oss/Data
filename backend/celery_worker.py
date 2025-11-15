from celery import Celery
from tools import run_kmeans_tool, generate_correlation_heatmap_tool, run_linear_regression_tool, run_naive_bayes_tool
from typing import List, Dict, Any
import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score
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

        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)

        # Usar validación cruzada para una evaluación más robusta
        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        accuracy = scores.mean()

        mlflow.log_metric("cross_val_accuracy", accuracy)

        # Entrenar el modelo final en todos los datos para registrarlo
        model.fit(X, y)
        mlflow.sklearn.log_model(model, "random_forest_model")

        return {
            "message": "Modelo entrenado y registrado en MLflow con éxito.",
            "run_id": run_id,
            "accuracy": accuracy
        }

@celery_app.task
def train_svm_classifier_task(
    data: List[Dict[str, Any]], target: str, features: List[str], experiment_name: str, kernel: str = 'rbf', C: float = 1.0
) -> Dict[str, Any]:
    """Entrena un Support Vector Classifier y lo registra en MLflow."""
    df = pd.DataFrame(data)
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        X = df[features]
        y = df[target]

        mlflow.log_param("kernel", kernel)
        mlflow.log_param("C", C)

        model = SVC(kernel=kernel, C=C, random_state=42)

        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        accuracy = scores.mean()

        mlflow.log_metric("cross_val_accuracy", accuracy)

        model.fit(X, y)
        mlflow.sklearn.log_model(model, "svm_model")

        return {
            "message": "Modelo SVM entrenado y registrado en MLflow con éxito.",
            "run_id": run_id,
            "accuracy": accuracy
        }


@celery_app.task
def train_decision_tree_classifier_task(
    data: List[Dict[str, Any]], target: str, features: List[str], experiment_name: str, max_depth: int = None
) -> Dict[str, Any]:
    """Entrena un DecisionTreeClassifier y lo registra en MLflow."""
    df = pd.DataFrame(data)
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        X = df[features]
        y = df[target]

        mlflow.log_param("max_depth", max_depth or "None")

        model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)

        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        accuracy = scores.mean()

        mlflow.log_metric("cross_val_accuracy", accuracy)

        model.fit(X, y)
        mlflow.sklearn.log_model(model, "decision_tree_model")

        return {
            "message": "Modelo de Árbol de Decisión entrenado y registrado en MLflow con éxito.",
            "run_id": run_id,
            "accuracy": accuracy
        }


@celery_app.task
def train_mlp_classifier_task(
    data: List[Dict[str, Any]], target: str, features: List[str], experiment_name: str
) -> Dict[str, Any]:
    """Entrena un MLPClassifier y lo registra en MLflow."""
    df = pd.DataFrame(data)
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        X = df[features]
        y = df[target]

        model = MLPClassifier(random_state=42, max_iter=500)

        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        accuracy = scores.mean()

        mlflow.log_metric("cross_val_accuracy", accuracy)

        model.fit(X, y)
        mlflow.sklearn.log_model(model, "mlp_model")

        return {
            "message": "Modelo MLP entrenado y registrado en MLflow con éxito.",
            "run_id": run_id,
            "accuracy": accuracy
        }


@celery_app.task
def run_arima_forecast_task(
    data: List[Dict[str, Any]], date_column: str, value_column: str, steps: int
) -> Dict[str, Any]:
    """Ejecuta un pronóstico ARIMA y devuelve los resultados."""
    from statsmodels.tsa.arima.model import ARIMA

    df = pd.DataFrame(data)
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.set_index(date_column)

    series = df[value_column]

    # Simple order selection (p,d,q). Could be improved with auto_arima.
    model = ARIMA(series, order=(5,1,0))
    model_fit = model.fit()

    forecast = model_fit.forecast(steps=steps)

    return {
        "message": f"Pronóstico de {steps} pasos completado.",
        "forecast": forecast.to_dict()
    }


@celery_app.task
def explain_model_features_task(
    run_id: str, data: List[Dict[str, Any]], features: List[str]
) -> Dict[str, Any]:
    """Carga un modelo de MLflow y genera un gráfico de importancia de características SHAP."""
    import shap
    import matplotlib.pyplot as plt
    import io
    import base64

    # Cargar modelo desde MLflow
    logged_model = f"runs:/{run_id}/random_forest_model" # Asume un nombre de modelo común
    try:
        model = mlflow.sklearn.load_model(logged_model)
    except Exception:
        # Intenta con otros nombres de modelo si falla
        try:
            model = mlflow.sklearn.load_model(f"runs:/{run_id}/svm_model")
        except Exception:
            try:
                model = mlflow.sklearn.load_model(f"runs:/{run_id}/decision_tree_model")
            except Exception:
                model = mlflow.sklearn.load_model(f"runs:/{run_id}/mlp_model")


    df = pd.DataFrame(data)
    X = df[features]

    # Usar SHAP para explicar el modelo
    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)

    # Generar el gráfico de resumen
    fig, ax = plt.subplots()
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return {
        "message": "Análisis de importancia de características completado.",
        "plot_base64": plot_base64
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
