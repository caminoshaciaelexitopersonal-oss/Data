import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
from backend.wpa.schemas import WpaAutoAnalysisRequest

# Sample data for mocking responses
SAMPLE_DF = pd.DataFrame([{"col1": 1, "col2": "a"}])
SAMPLE_EDA_REPORT = {"status": "success", "advanced_statistics": {}, "plots_base64": {}}

@patch('backend.wpa.auto_analysis.api.WpaAutoAnalysisService')
def test_wpa_auto_analysis_endpoint(mock_wpa_service, client):
    """
    Tests the /wpa/auto-analysis endpoint.
    Mocks the entire WPA service to test the API layer and orchestration call.
    """
    # Configure the mock to return a valid EDA report
    mock_instance = mock_wpa_service.return_value
    mock_instance.execute.return_value = SAMPLE_EDA_REPORT

    # Define the request payload
    request_data = {
        "source_type": "file",
        "data": [{"col1": 1, "col2": "a"}],
        "etl_steps": [{"action": "rename", "parameters": {"columns": {"col1": "new_col"}}}]
    }

    # Make the request
    response = client.post("/wpa/auto-analysis", json=request_data)

    # Assertions
    assert response.status_code == 200
    json_response = response.json()
    assert "job_id" in json_response
    assert json_response["message"] == "Automated analysis workflow completed successfully."
    assert json_response["eda_report"] == SAMPLE_EDA_REPORT

    # Verify that the service's execute method was called once
    mock_instance.execute.assert_called_once()
