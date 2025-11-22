
import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient

from fastapi import FastAPI
from backend.mpa.quality.api import router as quality_router

# Create a minimal app for testing the new endpoint
app = FastAPI()
app.include_router(quality_router)
client = TestClient(app)

@pytest.fixture
def sample_dataframe():
    """Provides a DataFrame with known quality issues."""
    data = {
        'col_a': [1, 2, 3, 4, 5, 6],
        'col_b': [1, 2, 3, np.nan, 5, 6],
        'col_c': [10, 20, 30, 40, 50, 500] # 500 is an outlier
    }
    df = pd.DataFrame(data)
    # Add one full duplicate row
    return pd.concat([df, df.iloc[[0]]], ignore_index=True)


@pytest.fixture
def sample_json_data(sample_dataframe):
    """Provides the sample data as JSON."""
    return sample_dataframe.replace({np.nan: None}).to_dict(orient="records")


# --- Unit Tests for the Service ---
from backend.services.data_quality_service import DataQualityService

def test_calculate_missing_values(sample_dataframe):
    service = DataQualityService()
    report = service._calculate_missing_values(sample_dataframe)
    assert report["total_missing"] == 1
    assert report["missing_percentage"] == pytest.approx(4.76, 0.01)
    assert report["missing_by_column"] == {"col_b": 1}

def test_calculate_duplicate_rows(sample_dataframe):
    service = DataQualityService()
    report = service._calculate_duplicate_rows(sample_dataframe)
    assert report["total_duplicates"] == 1
    assert report["duplicate_percentage"] == pytest.approx(14.28, 0.01)

def test_detect_outliers(sample_dataframe):
    service = DataQualityService()
    report = service._detect_outliers(sample_dataframe)
    assert report["total_outliers"] == 1
    assert report["outliers_by_column"] == {"col_c": 1}

def test_calculate_quality_score(sample_dataframe):
    service = DataQualityService()
    # Get the metrics first
    missing = service._calculate_missing_values(sample_dataframe)
    duplicates = service._calculate_duplicate_rows(sample_dataframe)
    outliers = service._detect_outliers(sample_dataframe)

    score = service._calculate_quality_score(sample_dataframe, missing, duplicates, outliers)
    assert score == pytest.approx(92.38, 0.01)

def test_generate_suggestions(sample_dataframe):
    service = DataQualityService()
    missing = service._calculate_missing_values(sample_dataframe)
    duplicates = service._calculate_duplicate_rows(sample_dataframe)
    outliers = service._detect_outliers(sample_dataframe)

    suggestions = service._generate_suggestions(missing, duplicates, outliers)
    assert len(suggestions) == 3

# --- Integration Test for the API Endpoint ---

def test_quality_report_endpoint(sample_json_data):
    """Tests the full /mpa/quality/report endpoint."""
    response = client.post("/mpa/quality/report", json={"data": sample_json_data})

    assert response.status_code == 200

    data = response.json()
    assert "quality_score" in data
    assert data["quality_score"] == pytest.approx(92.38, 0.01)
    assert data["metrics"]["duplicate_rows"]["total_duplicates"] == 1
    assert data["metrics"]["outliers"]["total_outliers"] == 1
    assert len(data["suggestions"]) == 3

def test_quality_report_endpoint_no_data():
    response = client.post("/mpa/quality/report", json={"data": []})
    assert response.status_code == 400
    assert response.json() == {"detail": "No data provided."}
