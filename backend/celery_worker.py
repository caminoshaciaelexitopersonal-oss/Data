from backend.celery_app import create_celery_app
from typing import List, Dict, Any
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
import httpx
import mlflow
import base64
import io
import matplotlib.pyplot as plt
import shap

# Import tools and services
from backend.legacy_tools import run_kmeans_tool, generate_correlation_heatmap_tool, run_linear_regression_tool, run_naive_bayes_tool
from backend.pipeline import run_pipeline as execute_etl_pipeline
from backend.app.services.etl_multisource_service import run_full_etl_process

# Create celery app instance using the factory
celery_app = create_celery_app()

# --- Task Definitions ---

@celery_app.task(queue='queue_etl')
def fetch_api_data_task(url: str) -> List[Dict[str, Any]]:
    try:
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise Exception(f"Error de red al acceder a la API: {e}")
    except Exception as e:
        raise Exception(f"Error al procesar la respuesta de la API: {e}")

@celery_app.task(queue='queue_model')
def run_kmeans_task(data: List[Dict[str, Any]], k: int, features: List[str]) -> Dict[str, Any]:
    return run_kmeans_tool(data, k, features, random_state=42)

@celery_app.task(queue='queue_eda')
def generate_correlation_heatmap_task(data: List[Dict[str, Any]]) -> Dict[str, str]:
    return generate_correlation_heatmap_tool(data)

@celery_app.task(queue='queue_model')
def run_linear_regression_task(data: List[Dict[str, Any]], target: str, feature: str) -> Dict[str, Any]:
    return run_linear_regression_tool(data, target, feature)

@celery_app.task(queue='queue_model')
def run_naive_bayes_task(data: List[Dict[str, Any]], target: str, features: List[str]) -> Dict[str, Any]:
    return run_naive_bayes_tool(data, target, features)

@celery_app.task(queue='queue_model')
def train_random_forest_classifier_task(
    data: List[Dict[str, Any]], target: str, features: List[str], experiment_name: str
) -> Dict[str, Any]:
    df = pd.DataFrame(data)
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        X = df[features]
        y = df[target]
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        accuracy = scores.mean()
        mlflow.log_metric("cross_val_accuracy", accuracy)
        model.fit(X, y)
        mlflow.sklearn.log_model(model, "random_forest_model")
        return {"run_id": run_id, "accuracy": accuracy}

# ... (todas las demás definiciones de tareas se mantienen igual)
@celery_app.task(queue='queue_model')
def train_svm_classifier_task(
    data: List[Dict[str, Any]], target: str, features: List[str], experiment_name: str, kernel: str = 'rbf', C: float = 1.0
) -> Dict[str, Any]:
    df = pd.DataFrame(data)
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        X = df[features]
        y = df[target]
        model = SVC(kernel=kernel, C=C, random_state=42)
        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        accuracy = scores.mean()
        mlflow.log_metric("cross_val_accuracy", accuracy)
        model.fit(X, y)
        mlflow.sklearn.log_model(model, "svm_model")
        return {"run_id": run_id, "accuracy": accuracy}

@celery_app.task(queue='queue_model')
def train_decision_tree_classifier_task(
    data: List[Dict[str, Any]], target: str, features: List[str], experiment_name: str, max_depth: int = None
) -> Dict[str, Any]:
    df = pd.DataFrame(data)
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        X = df[features]
        y = df[target]
        model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        accuracy = scores.mean()
        mlflow.log_metric("cross_val_accuracy", accuracy)
        model.fit(X, y)
        mlflow.sklearn.log_model(model, "decision_tree_model")
        return {"run_id": run_id, "accuracy": accuracy}

@celery_app.task(queue='queue_model')
def train_mlp_classifier_task(
    data: List[Dict[str, Any]], target: str, features: List[str], experiment_name: str
) -> Dict[str, Any]:
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
        return {"run_id": run_id, "accuracy": accuracy}

@celery_app.task(queue='queue_model')
def run_arima_forecast_task(
    data: List[Dict[str, Any]], date_column: str, value_column: str, steps: int
) -> Dict[str, Any]:
    from statsmodels.tsa.arima.model import ARIMA
    df = pd.DataFrame(data)
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.set_index(date_column)
    series = df[value_column]
    model = ARIMA(series, order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)
    return {"forecast": forecast.to_dict()}

@celery_app.task(queue='queue_model')
def explain_model_features_task(
    run_id: str, data: List[Dict[str, Any]], features: List[str]
) -> Dict[str, Any]:
    logged_model = f"runs:/{run_id}/random_forest_model"
    try:
        model = mlflow.sklearn.load_model(logged_model)
    except Exception:
        model = mlflow.sklearn.load_model(f"runs:/{run_id}/svm_model")
    df = pd.DataFrame(data)
    X = df[features]
    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)
    fig, ax = plt.subplots()
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return {"plot_base64": plot_base64}

@celery_app.task(queue='queue_etl')
def run_etl_pipeline_task(data: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    df = pd.DataFrame(data)
    transformed_df = execute_etl_pipeline(df, steps)
    return transformed_df.to_dict(orient='records')

@celery_app.task(name='celery_worker.process_multiple_files_task', queue='queue_etl')
def process_multiple_files_task(file_contents: Dict[str, bytes]) -> Dict[str, Any]:
    try:
        result = run_full_etl_process(file_contents)
        return {"status": "SUCCESS", "results": result}
    except Exception as e:
        raise e
