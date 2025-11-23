import requests
import os

# --- Configuration ---
BASE_URL = "http://localhost:8000/unified/v1"
TEST_FILE_PATH = "test_data.csv"

def create_test_file():
    """Creates a simple CSV file for testing."""
    with open(TEST_FILE_PATH, "w") as f:
        f.write("id,value\n")
        f.write("1,100\n")
        f.write("2,200\n")

def run_e2e_test():
    """Runs the end-to-end test for the unified session-based workflow."""

    print("--- Starting E2E Test ---")

    # --- Step 1: Create Session ---
    try:
        print("Step 1: Creating a new session...")
        response = requests.post(f"{BASE_URL}/mcp/session/create")
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data.get("session_id")
        assert session_id, f"Failed to get session_id from response: {session_data}"
        print(f"-> SUCCESS: Session created with ID: {session_id}")
    except requests.exceptions.RequestException as e:
        print(f"-> FAILED: Could not create session. Error: {e}")
        return

    # --- Step 2: Upload File ---
    try:
        print("\nStep 2: Uploading a file to the session...")
        with open(TEST_FILE_PATH, "rb") as f:
            files = {"file": (TEST_FILE_PATH, f, "text/csv")}
            data = {"session_id": session_id}
            response = requests.post(f"{BASE_URL}/mpa/ingestion/upload-file/", files=files, data=data)
            response.raise_for_status()
            upload_data = response.json()
            assert upload_data.get("filename") == TEST_FILE_PATH, f"Unexpected filename in response: {upload_data}"
            print(f"-> SUCCESS: File '{upload_data.get('filename')}' uploaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"-> FAILED: Could not upload file. Error: {e}")
        return

    # --- Step 3: Get Quality Report ---
    try:
        print("\nStep 3: Requesting a data quality report for the session...")
        response = requests.post(f"{BASE_URL}/mpa/quality/report", json={"session_id": session_id})
        response.raise_for_status()
        report_data = response.json()
        assert "quality_score" in report_data, f"Quality score not found in report: {report_data}"
        print(f"-> SUCCESS: Quality report generated. Quality Score: {report_data.get('quality_score')}")
    except requests.exceptions.RequestException as e:
        print(f"-> FAILED: Could not get quality report. Error: {e}")
        return

    print("\n--- E2E Test Completed Successfully ---")

if __name__ == "__main__":
    create_test_file()
    run_e2e_test()
    os.remove(TEST_FILE_PATH)
