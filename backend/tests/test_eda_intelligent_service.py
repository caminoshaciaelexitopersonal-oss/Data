
import pytest
import pandas as pd
from fastapi.testclient import TestClient
import base64

from fastapi import FastAPI
from backend.mpa.eda.api import router as eda_router

app = FastAPI()
app.include_router(eda_router)

client = TestClient(app)

@pytest.fixture
def sample_dataframe():
    """Provides a sample DataFrame for testing."""
    data = {
        'numeric_col': [1, 2, 3, 4, 100],  # 100 is an outlier
        'categorical_col': ['A', 'B', 'A', 'C', 'B'],
        'constant_col': [1, 1, 1, 1, 1]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_json_data():
    """Provides the sample data as JSON, mimicking a request body."""
    return [
        {'numeric_col': 1, 'categorical_col': 'A', 'constant_col': 1},
        {'numeric_col': 2, 'categorical_col': 'B', 'constant_col': 1},
        {'numeric_col': 3, 'categorical_col': 'A', 'constant_col': 1},
        {'numeric_col': 4, 'categorical_col': 'C', 'constant_col': 1},
        {'numeric_col': 100, 'categorical_col': 'B', 'constant_col': 1}
    ]

# --- Unit Tests for the Service ---
from backend.services.eda_intelligent_service import EdaIntelligentService

def test_auto_summary(sample_dataframe):
    service = EdaIntelligentService()
    summary = service.auto_summary(sample_dataframe)
    assert summary["shape"] == (5, 3)
    assert summary["duplicate_rows"] == 0
    assert "numeric_col" in summary["column_details"]
    assert "mean" in summary["column_details"]["numeric_col"]
    assert summary["column_details"]["numeric_col"]["mean"] == 22.0

def test_auto_detect_distributions(sample_dataframe):
    service = EdaIntelligentService()
    distributions = service.auto_detect_distributions(sample_dataframe)
    assert "numeric_col" in distributions
    assert distributions["numeric_col"] == "Not Normally Distributed"
    assert distributions["constant_col"] == "Constant Value"

def test_auto_detect_outliers(sample_dataframe):
    service = EdaIntelligentService()
    outliers = service.auto_detect_outliers(sample_dataframe)
    assert "numeric_col" in outliers
    assert outliers["numeric_col"]["count"] == 1
    assert outliers["numeric_col"]["values"] == [100]

def test_auto_visualizations(sample_dataframe):
    service = EdaIntelligentService()
    visualizations = service.auto_visualizations(sample_dataframe)
    assert len(visualizations) == 3 # 2 numeric histograms, 1 categorical bar chart

    # Check that a visualization has the correct structure
    histo = next(v for v in visualizations if v["title"] == "Distribution of numeric_col")
    assert histo["chart_type"] == "histogram"
    assert "image_base64" in histo
    # Check if the base64 string is valid
    base64.b64decode(histo["image_base64"])


# --- Integration Test for the API Endpoint ---

def test_intelligent_eda_endpoint(sample_json_data):
    """
    Tests the full /mpa/eda/intelligent endpoint.
    """
    response = client.post("/mpa/eda/intelligent", json=sample_json_data)

    assert response.status_code == 200

    data = response.json()
    assert data["summary"]["shape"] == [5, 3]
    assert data["outliers"]["numeric_col"]["count"] == 1
    assert data["outliers"]["numeric_col"]["values"] == [100]
    assert len(data["visualizations"]) == 3

def test_intelligent_eda_endpoint_empty_data():
    response = client.post("/mpa/eda/intelligent", json=[])
    assert response.status_code == 400
    assert response.json() == {"detail": "No data provided."}
