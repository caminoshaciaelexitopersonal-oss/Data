import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Since the app and other dependencies are set up in conftest.py,
# we just need to import the client fixture.

def test_get_logged_steps(client):
    """
    Tests the /get-steps endpoint.
    This assumes that some other action has logged steps.
    For a pure unit test, we might want to call log_step directly.
    """
    # Let's clear and add a step to be sure.
    from backend.logger import clear_log, log_step
    clear_log()
    log_step("Test Step", "print('hello')")

    response = client.get("/api/v1/get-steps")
    assert response.status_code == 200
    assert len(response.json()["steps"]) == 1
    assert response.json()["steps"][0]["description"] == "Test Step"

def test_visualizations_endpoint(client):
    """
    Tests the /api/visualizations endpoint.
    """
    from backend.visualizations import clear_visualizations, add_visualization
    clear_visualizations()
    add_visualization("my_chart", {"type": "bar", "data": [1, 2, 3]})

    response = client.get("/api/v1/visualizations")
    assert response.status_code == 200
    assert "my_chart" in response.json()
    assert response.json()["my_chart"]["type"] == "bar"

def test_download_report_endpoint(client):
    """
    Tests the /download-report endpoint.
    """
    from backend.report_generator import clear_report_artifacts, set_summary
    clear_report_artifacts()
    set_summary("This is a test summary for the report.")

    response = client.get("/api/v1/download-report")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert len(response.content) > 0

@patch('backend.main.PlanAndExecute.ainvoke')
def test_chat_agent_endpoint(mock_ainvoke, client):
    """
    Tests the /chat/agent endpoint with a mocked LLM agent.
    """
    mock_ainvoke.return_value = {"output": "Mocked agent response."}

    chat_req = {
        "message": "Analyze this data",
        "data": [{"col1": 1, "col2": 2}],
        "llm_preference": "gemini"
    }

    response = client.post("/api/v1/chat/agent/", json=chat_req)

    assert response.status_code == 200
    assert "output" in response.json()
    assert response.json()["output"] == "Mocked agent response."

def test_export_code_endpoint(client):
    """
    Tests the /export/code endpoint.
    """
    from backend.logger import clear_log, log_step
    clear_log()
    log_step("Test export step", "import pandas as pd")

    response = client.get("/api/v1/export/code")

    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/zip'
    assert len(response.content) > 0
