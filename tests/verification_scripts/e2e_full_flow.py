import requests
import os

BASE_URL = "http://localhost:8000"
TEST_FILE = "test_data.csv"

def run_e2e_test():
    session_id = None
    try:
        # --- Step 1: Create a new session ---
        print("Step 1: Creating session...")
        response = requests.post(f"{BASE_URL}/unified/v1/mcp/session/create")
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data.get("session_id")
        assert session_id, "Session ID not found in response"
        print(f"SUCCESS: Session created with ID: {session_id}")

        # --- Step 2: Upload a file ---
        print("\nStep 2: Uploading file...")
        with open(TEST_FILE, 'rb') as f:
            files = {'file': (TEST_FILE, f, 'text/csv')}
            data = {'session_id': session_id}
            response = requests.post(f"{BASE_URL}/unified/v1/mpa/ingestion/upload-file/", files=files, data=data)
            response.raise_for_status()
        upload_data = response.json()
        assert upload_data.get("filename") == TEST_FILE, "Filename mismatch in upload response"
        print(f"SUCCESS: File '{TEST_FILE}' uploaded successfully.")

        # --- Step 3: Get a quality report ---
        print("\nStep 3: Requesting data quality report...")
        json_payload = {"session_id": session_id}
        response = requests.post(f"{BASE_URL}/unified/v1/mpa/quality/report", json=json_payload)
        response.raise_for_status()
        quality_data = response.json()
        assert "health_score" in quality_data, "Health score not in quality report"
        print(f"SUCCESS: Quality report received. Health Score: {quality_data['health_score']}")

        # --- Step 4: Chat with the agent ---
        print("\nStep 4: Chatting with the agent...")
        chat_payload = {
            "session_id": session_id,
            "message": "Who is the oldest person in the dataset?"
        }
        response = requests.post(f"{BASE_URL}/unified/v1/chat", json=chat_payload)
        response.raise_for_status()
        chat_response = response.json()
        agent_output = chat_response.get("output", "").lower()
        assert "marta" in agent_output, f"Expected 'Marta' in agent response, but got: {agent_output}"
        print(f"SUCCESS: Agent correctly identified Marta. Response: '{chat_response.get('output')}'")

        print("\n--- E2E TEST PASSED ---")

    except requests.exceptions.RequestException as e:
        print(f"\n--- E2E TEST FAILED ---")
        print(f"Request failed: {e.request.method} {e.request.url}")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")
        else:
            print("The backend service may not be running or is unreachable.")
    except AssertionError as e:
        print(f"\n--- E2E TEST FAILED ---")
        print(f"Assertion failed: {e}")

if __name__ == "__main__":
    run_e2e_test()
