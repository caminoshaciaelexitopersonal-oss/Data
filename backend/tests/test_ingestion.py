import pytest
import io

def test_upload_valid_csv(client):
    """
    Tests uploading a valid CSV file.
    """
    csv_content = "col1,col2\n1,2\n3,4"
    file_bytes = io.BytesIO(csv_content.encode('utf-8'))
    response = client.post(
        "/api/v1/upload-data/",
        files={"file": ("test.csv", file_bytes, "text/csv")}
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["filename"] == "test.csv"
    assert len(json_response["data"]) == 2

def test_upload_file_too_large(client):
    """
    Tests attempting to upload a file that exceeds the maximum size limit.
    """
    # Create a dummy file that is slightly larger than the limit (100 MB)
    large_content = b"a" * (101 * 1024 * 1024)
    file_bytes = io.BytesIO(large_content)
    response = client.post(
        "/api/v1/upload-data/",
        files={"file": ("large_file.txt", file_bytes, "text/plain")}
    )
    assert response.status_code == 413
    assert "El archivo es demasiado grande" in response.json()["detail"]

def test_upload_invalid_mimetype(client):
    """
    Tests attempting to upload a file with an unsupported MIME type.
    """
    # Simulate a file with a misleading extension but correct (disallowed) content
    exe_content = b"\x4d\x5a" # MZ executable header
    file_bytes = io.BytesIO(exe_content)
    response = client.post(
        "/api/v1/upload-data/",
        files={"file": ("test.csv", file_bytes, "application/octet-stream")}
    )
    assert response.status_code == 415
    assert "Tipo de archivo no soportado o corrupto" in response.json()["detail"]

def test_upload_sql_with_denylisted_keyword(client):
    """
    Tests the SQL query sanitization to prevent dangerous commands.
    """
    response = client.post(
        "/api/v1/load-from-db/",
        json={"db_uri": "sqlite:///:memory:", "query": "DROP TABLE users;"}
    )
    assert response.status_code == 403
    assert "La consulta SQL contiene comandos no permitidos" in response.json()["detail"]
