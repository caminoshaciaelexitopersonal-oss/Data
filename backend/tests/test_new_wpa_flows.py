import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4

# Use the client fixture from conftest.py
def test_wpa_modeling_train_endpoint(client: TestClient):
    job_id = str(uuid4())
    request_data = {
        "job_id": job_id,
        "model_type": "random_forest",
        "target_column": "species",
        "feature_columns": ["sepal_length", "sepal_width"],
        "session_id": "session-123"
    }

    with patch('backend.wpa.modeling.api.ModelingService') as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.train_model.return_value = {
            "mlflow_run_id": "mock_run_id",
            "model_accuracy": 0.95
        }

        response = client.post("/wpa/modeling/train", json=request_data)

        assert response.status_code == 200
        json_res = response.json()
        assert json_res["job_id"] == job_id
        assert json_res["mlflow_run_id"] == "mock_run_id"
        assert json_res["model_accuracy"] == 0.95
        mock_instance.train_model.assert_called_once()


def test_wpa_report_generation_endpoint(client: TestClient):
    job_id = str(uuid4())
    request_data = {
        "job_id": job_id,
        "title": "Test Report",
        "summary": "This is a test summary."
    }

    with patch('backend.wpa.report_generation.api.ReportGenerationService') as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.generate_report.return_value = {"file_path": "test_report.docx"}

        response = client.post("/wpa/reports/generate", json=request_data)

        assert response.status_code == 200
        json_res = response.json()
        assert json_res["job_id"] == job_id
        assert "report_url" in json_res
        mock_instance.generate_report.assert_called_once()

def test_wpa_db_ingestion_endpoint(client: TestClient):
    job_id = str(uuid4())
    request_data = {
        "job_id": job_id,
        "db_uri": "sqlite:///:memory:",
        "sql_query": "SELECT 1"
    }

    with patch('backend.wpa.db_ingestion.api.DbIngestionService') as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.ingest_from_db.return_value = {
            "session_id": "new-session-id",
            "data_preview": [{"col1": 1}]
        }

        response = client.post("/wpa/ingestion/from-db", json=request_data)

        assert response.status_code == 200
        json_res = response.json()
        assert json_res["job_id"] == job_id
        assert json_res["session_id"] == "new-session-id"
        mock_instance.ingest_from_db.assert_called_once()
