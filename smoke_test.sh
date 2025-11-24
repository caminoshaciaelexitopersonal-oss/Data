#!/bin/bash

# Define the base URL for the backend
BASE_URL="http://localhost:8000"

# --- Step 1: Create a new session ---
echo "--- Creating new session ---"
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/unified/v1/mcp/session/create")
SESSION_ID=$(echo "$SESSION_RESPONSE" | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$SESSION_ID" ]; then
    echo "ERROR: Failed to create session. Response was:"
    echo "$SESSION_RESPONSE"
    exit 1
fi

echo "Session created with ID: $SESSION_ID"
echo ""

# --- Step 2: Upload CSV file ---
echo "--- Uploading CSV file ---"
UPLOAD_CSV_RESPONSE=$(curl -s -X POST \
  -F "session_id=$SESSION_ID" \
  -F "file=@test_data.csv;type=text/csv" \
  "$BASE_URL/unified/v1/mpa/ingestion/upload-file/")

if [[ $(echo "$UPLOAD_CSV_RESPONSE" | grep -c '"filename":"test_data.csv"') -eq 0 ]]; then
    echo "ERROR: Failed to upload CSV. Response was:"
    echo "$UPLOAD_CSV_RESPONSE"
    exit 1
fi

echo "CSV file uploaded successfully."
echo "$UPLOAD_CSV_RESPONSE"
echo ""


# --- Step 3: Upload XLSX file ---
echo "--- Uploading XLSX file ---"
UPLOAD_XLSX_RESPONSE=$(curl -s -X POST \
  -F "session_id=$SESSION_ID" \
  -F "file=@test_data.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  "$BASE_URL/unified/v1/mpa/ingestion/upload-file/")

if [[ $(echo "$UPLOAD_XLSX_RESPONSE" | grep -c '"filename":"test_data.xlsx"') -eq 0 ]]; then
    echo "ERROR: Failed to upload XLSX. Response was:"
    echo "$UPLOAD_XLSX_RESPONSE"
    exit 1
fi

echo "XLSX file uploaded successfully."
echo "$UPLOAD_XLSX_RESPONSE"
echo ""

# --- Step 4: Query the agent ---
echo "--- Querying the agent about the data ---"
AGENT_QUERY_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"Basado en todos los datos cargados, ¿cuántas filas hay en total?\"}" \
  "$BASE_URL/unified/v1/chat")

echo "Agent response:"
echo "$AGENT_QUERY_RESPONSE"
echo ""

# --- Final Validation ---
if [[ $(echo "$AGENT_QUERY_RESPONSE" | grep -c '"output"') -gt 0 ]]; then
    echo "--- SMOKE TEST PASSED ---"
    echo "The agent responded, implying the ETL flow (ingest -> store -> read) is working."
else
    echo "--- SMOKE TEST FAILED ---"
    echo "The agent did not provide a valid response."
fi
