#!/bin/bash

# Define the base URL for the backend
BASE_URL="http://localhost:8000"

echo "--- STARTING CONTEXT VERIFICATION SMOKE TEST ---"
echo ""

# --- Step 1: Create a new session ---
echo "1. Creating new session..."
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/unified/v1/mcp/session/create")
SESSION_ID=$(echo "$SESSION_RESPONSE" | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$SESSION_ID" ]; then
    echo "   ERROR: Failed to create session. Aborting."
    exit 1
fi
echo "   SUCCESS: Session created with ID: $SESSION_ID"
echo ""

# --- Step 2: Upload CSV file ---
echo "2. Uploading population data (poblacion.csv)..."
UPLOAD_RESPONSE=$(curl -s -X POST \
  -F "session_id=$SESSION_ID" \
  -F "file=@poblacion.csv;type=text/csv" \
  "$BASE_URL/unified/v1/mpa/ingestion/upload-file/")

if [[ $(echo "$UPLOAD_RESPONSE" | grep -c '"filename":"poblacion.csv"') -eq 0 ]]; then
    echo "   ERROR: Failed to upload CSV. Aborting."
    echo "   Response: $UPLOAD_RESPONSE"
    exit 1
fi
echo "   SUCCESS: File uploaded and ingested."
echo ""

# --- Step 3: Ask the agent a context-based question ---
echo "3. Asking the agent: '¿Cuál es la ciudad con mayor población?'"
AGENT_QUERY_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"¿Cuál es la ciudad con mayor población según los datos?\"}" \
  "$BASE_URL/unified/v1/chat")

echo "   Agent Response: $AGENT_QUERY_RESPONSE"
echo ""

# --- Step 4: Verify the response ---
echo "4. Verifying the response..."
# We check if the response contains "Madrid", which is the correct answer from the data context.
if [[ $(echo "$AGENT_QUERY_RESPONSE" | grep -ci 'Madrid') -gt 0 ]]; then
    echo "   SUCCESS: Agent correctly identified the city with the highest population."
    echo ""
    echo "--- SMOKE TEST PASSED ---"
else
    echo "   ERROR: Agent response did not contain the expected answer ('Madrid')."
    echo ""
    echo "--- SMOKE TEST FAILED ---"
    exit 1
fi
