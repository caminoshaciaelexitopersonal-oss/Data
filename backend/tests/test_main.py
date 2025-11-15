import pytest
from fastapi.testclient import TestClient
import pandas as pd
import io
from unittest.mock import patch, MagicMock

from ..main import app
from ..logger import clear_log, log_step, get_logged_steps
from ..visualizations import clear_visualizations, add_visualization, get_all_visualizations, get_mock_visualizations
from ..pipeline import run_pipeline
from ..report_generator import clear_report_artifacts, set_summary
from ..app.export import code_exporter

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

    clear_report_artifacts()
    set_summary("Este es un resumen de prueba.")
    response = client.get("/download-report")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert len(response.content) > 0

# --- Pruebas para Herramientas (con mocks) ---

@patch('backend.main.fetch_api_data_task.delay')
def test_fetch_api_data_tool(mock_delay):
    from ..main import fetch_api_data
    mock_task = MagicMock()
    mock_task.get.return_value = [{"id": 1, "value": 100}]
    mock_delay.return_value = mock_task

    clear_visualizations()
    result = fetch_api_data("http://fakeapi.com/data")

    assert "data" in result
    assert "etl_summary" in get_all_visualizations()

# --- Nuevas Pruebas para Endpoints Faltantes ---

@patch('backend.main.get_llm_for_agent')
def test_chat_agent_endpoint(mock_get_llm):
    mock_llm = MagicMock()
    # LangChain's PlanAndExecute can be complex to mock. We'll mock the final invoke.
    with patch('backend.main.PlanAndExecute.ainvoke') as mock_ainvoke:
        mock_ainvoke.return_value = {"output": "Respuesta simulada del agente."}

        chat_req = {
            "message": "Analiza estos datos",
            "data": [{"col1": 1, "col2": 2}],
            "llm_preference": "gemini"
        }

        response = client.post("/chat/agent/", json=chat_req)

        assert response.status_code == 200
        assert "output" in response.json()
        assert response.json()["output"] == "Respuesta simulada del agente."

def test_audit_log_endpoint():
    response = client.get("/audit-log")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_export_code_endpoint():
    clear_log()
    log_step("Paso de prueba", "print('hola')")

    response = client.get("/export/code")

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/zip'
    assert len(response.content) > 0
