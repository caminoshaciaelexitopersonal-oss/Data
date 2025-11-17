
import pytest
import pandas as pd
from fastapi.testclient import TestClient

from fastapi import FastAPI
from backend.mpa.ml.api import router as ml_router

app = FastAPI()
app.include_router(ml_router)
client = TestClient(app)

@pytest.fixture
def sample_anomaly_data():
    """Provides a DataFrame with obvious anomalies."""
    data = {
        'feature1': [1.0, 1.1, 1.2, 1.0, 0.9, 1.3, 10.0], # 10.0 is an anomaly
        'feature2': [2.0, 2.2, 1.9, 2.1, 2.0, 1.8, -5.0], # -5.0 is an anomaly
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_anomaly_json_request(sample_anomaly_data):
    """Provides a sample JSON request body for the API."""
    return {
        "data": sample_anomaly_data.to_dict(orient="records"),
        "columns": ["feature1", "feature2"],
        "contamination": 0.2 # Expecting 2 anomalies out of 7 data points approx
    }

# --- Unit Tests for the Service ---
from backend.services.anomaly_service import AnomalyService

def test_detect_anomalies(sample_anomaly_data):
    service = AnomalyService()
    result = service.detect_anomalies(sample_anomaly_data, columns=['feature1', 'feature2'])

    assert "anomalies_indices" in result
    assert "scores" in result
    assert len(result["scores"]) == len(sample_anomaly_data)
    # With a contamination of 0.1, we expect 1 anomaly (10% of 7 is 0.7, rounds to 1)
    assert len(result["anomalies_indices"]) > 0
    # The most obvious anomalies should be detected
    assert 6 in result["anomalies_indices"] or 5 in result["anomalies_indices"]

# --- Integration Test for the API Endpoint ---

def test_anomaly_detection_endpoint(sample_anomaly_json_request):
    response = client.post("/mpa/ml/anomaly-detection", json=sample_anomaly_json_request)

    assert response.status_code == 200
    data = response.json()
    assert "anomalies_indices" in data
    assert "scores" in data
    assert len(data["anomalies_indices"]) > 0

def test_anomaly_detection_endpoint_no_columns():
    request_data = {"data": [{"a": 1}], "columns": []}
    response = client.post("/mpa/ml/anomaly-detection", json=request_data)
    assert response.status_code == 400
    assert "No columns specified" in response.json()["detail"]

def test_anomaly_detection_endpoint_bad_column_name():
    request_data = {"data": [{"a": 1}], "columns": ["non_existent_col"]}
    response = client.post("/mpa/ml/anomaly-detection", json=request_data)
    assert response.status_code == 400
    assert "not in the DataFrame" in response.json()["detail"]
