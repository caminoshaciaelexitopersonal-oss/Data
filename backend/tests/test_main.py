import pytest
from fastapi.testclient import TestClient
 
import pandas as pd
import io
from unittest.mock import patch, MagicMock
 

# Añadir el directorio raíz al path para que se pueda importar 'main'
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

 
# Importar la app de FastAPI
from main import app

# Importar explícitamente solo lo necesario
from logger import clear_log, log_step, get_logged_steps
from visualizations import clear_visualizations, add_visualization, get_all_visualizations, get_mock_visualizations
from pipeline import run_pipeline

client = TestClient(app)

# --- Pruebas Unitarias para Módulos ---

def test_logger_functions():
    clear_log()
    assert get_logged_steps() == []
    log_step("Paso 1", "code 1")
    assert len(get_logged_steps()) == 1
    clear_log()

def test_visualizations_functions():
    clear_visualizations()
    assert get_all_visualizations() == get_mock_visualizations()
    add_visualization("test_chart", [1])
    assert get_all_visualizations()["test_chart"] == [1]
    clear_visualizations()

def test_pipeline_runner():
    data = pd.DataFrame({"a": [1, None], "b": ["x", "y"]})
    steps = [{"action": "drop_nulls", "column": "a"}]
    transformed_df = run_pipeline(data, steps)
    assert transformed_df.shape[0] == 1

# --- Pruebas para Endpoints de FastAPI ---

def test_endpoints():
    clear_log()
    log_step("test", "code")
    response = client.get("/get-steps")
    assert response.status_code == 200
    assert len(response.json()["steps"]) == 1

    clear_visualizations()
    add_visualization("test_viz", [1])
    response = client.get("/api/visualizations")
    assert response.status_code == 200
    assert "test_viz" in response.json()

    pipeline_req = {
        "data": [{"a": 1}, {"a": None}],
        "steps": [{"action": "drop_nulls", "column": "a"}]
    }
    response = client.post("/run-pipeline/", json=pipeline_req)
    assert response.status_code == 200
    assert len(response.json()["processed_data"]) == 1

    clear_visualizations()
    csv_content = b"col1,col2\n1,2\n3,4"
    response = client.post("/upload-data/", files={"file": ("test.csv", io.BytesIO(csv_content), "text/csv")})
    assert response.status_code == 200
    viz_data = get_all_visualizations()
    assert "etl_summary" in viz_data

# --- Pruebas para Herramientas (con mocks) ---

@patch('main.fetch_api_data_task.delay')
def test_fetch_api_data_tool(mock_delay):
    from main import fetch_api_data # Importación local
    mock_task = MagicMock()
    mock_task.get.return_value = [{"id": 1, "value": 100}]
    mock_delay.return_value = mock_task

    clear_visualizations()
    result = fetch_api_data("http://fakeapi.com/data")

    assert "data" in result
    assert "etl_summary" in get_all_visualizations()
 
