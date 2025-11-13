import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pandas as pd
import io

# Añadir el directorio raíz al path para que se pueda importar 'main'
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from logger import clear_log, log_step, get_logged_steps
from visualizations import clear_visualizations, add_visualization, get_all_visualizations, get_mock_visualizations

client = TestClient(app)

# --- Pruebas para el Logger SADI ---

def test_logger_functions():
    """Prueba las funciones básicas del logger: limpiar, añadir y obtener."""
    clear_log()
    assert get_logged_steps() == []

    log_step("Paso de prueba 1", "print('Hola')")
    log_step("Paso de prueba 2", "x = 1+1")

    steps = get_logged_steps()
    assert len(steps) == 2
    assert steps[0]["descripcion"] == "Paso de prueba 1"
    assert steps[1]["codigo"] == "x = 1+1"

    clear_log()
    assert get_logged_steps() == []

def test_get_steps_endpoint():
    """Prueba el endpoint /get-steps."""
    clear_log()
    log_step("Paso de prueba para endpoint", "a=1")

    response = client.get("/get-steps")
    assert response.status_code == 200
    data = response.json()
    assert "steps" in data
    assert len(data["steps"]) == 1
    assert data["steps"][0]["descripcion"] == "Paso de prueba para endpoint"

# --- Pruebas para el Panel de Visualización Analítica (PVA) ---

def test_visualizations_functions():
    """Prueba las funciones básicas del módulo de visualizaciones."""
    clear_visualizations()
    assert get_all_visualizations() == get_mock_visualizations() # Debe devolver mock si está vacío

    add_visualization("test_chart", [{"x": 1, "y": 2}])

    viz = get_all_visualizations()
    assert "test_chart" in viz
    assert viz["test_chart"][0]["x"] == 1

    clear_visualizations()
    assert get_all_visualizations() == get_mock_visualizations()

def test_get_visualizations_endpoint():
    """Prueba el endpoint /api/visualizations."""
    clear_visualizations()
    add_visualization("test_viz_endpoint", [{"value": 100}])

    response = client.get("/api/visualizations")
    assert response.status_code == 200
    data = response.json()
    assert "test_viz_endpoint" in data
    assert data["test_viz_endpoint"][0]["value"] == 100

# --- Pruebas de Integración (simulando un flujo) ---

# Para probar el agente, necesitaríamos mockear la llamada al LLM,
# lo cual es más complejo. Por ahora, probaremos la integración
# de los logs y visualizaciones en los endpoints de datos.

def test_upload_data_generates_etl_visualization():
    """Prueba que la carga de datos genera y guarda la visualización 'etl_summary'."""
    clear_visualizations()

    # Crear un archivo CSV en memoria como bytes
    csv_content = b"col1,col2\n1,2\n3,4"
    file = ("test.csv", io.BytesIO(csv_content), "text/csv")

    response = client.post("/upload-data/", files={"file": file})
    assert response.status_code == 200

    viz_data = get_all_visualizations()
    assert "etl_summary" in viz_data
    summary = viz_data["etl_summary"]
    assert len(summary) == 2
    assert summary[0]["feature"] == "col1"
    assert summary[0]["mean"] == 2.0
