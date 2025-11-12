from celery import Celery
from tools import run_kmeans_tool, generate_correlation_heatmap_tool, run_linear_regression_tool, run_naive_bayes_tool
from typing import List, Dict, Any

# Configura Celery. Usa Redis como broker.
celery_app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

# Define las tareas asíncronas envolviendo las funciones de nuestras herramientas
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
