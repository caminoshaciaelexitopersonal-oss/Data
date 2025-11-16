import pytest

def test_run_etl_pipeline(client):
    """
    Tests the ETL pipeline by running a series of transformation steps.
    """
    test_data = [
        {"nombreCompleto": "Juan Pérez", "edad": 30, "ciudad": "Madrid"},
        {"nombreCompleto": "Ana García", "edad": None, "ciudad": "Barcelona"},
        {"nombreCompleto": "Luis Rodríguez", "edad": 25, "ciudad": "Madrid"},
    ]

    # Corrected pipeline steps format
    pipeline_steps = [
        {"action": "rename", "columns": {"nombreCompleto": "full_name"}},
        {"action": "drop_nulls", "column": "edad"},
    ]

    response = client.post(
        "/api/v1/run-pipeline/",
        json={"data": test_data, "steps": pipeline_steps}
    )

    assert response.status_code == 200
    processed_data = response.json()["processed_data"]

    assert len(processed_data) == 2
    assert "full_name" in processed_data[0]
    assert "nombreCompleto" not in processed_data[0]
    assert processed_data[0]["full_name"] == "Juan Pérez"
    assert processed_data[1]["full_name"] == "Luis Rodríguez"
