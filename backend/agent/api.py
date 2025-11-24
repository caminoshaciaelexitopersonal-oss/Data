from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from backend.llm import llm_router
from backend.app.services.state_store import StateStore, get_state_store

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
async def chat_agent(
    request: ChatRequest = Body(...),
    state_store: StateStore = Depends(get_state_store)
) -> Dict[str, Any]:
    """
    Handles a chat message by invoking the intelligent agent with the
    message and the context from the current session.
    """
    try:
        # Here you would typically load context, history, or data from the session
        # For now, we just pass the message to the LLM router.
        df = state_store.load_dataframe(session_id=request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for session_id: {request.session_id}. Please upload a file first.")

        # Construct a more informative prompt
        prompt = f"""
        Based on the user's request, analyze the following data snippet:
        {df.head().to_string()}

        User's request: "{request.message}"
        """

        # Use the LLM router to get a response
        response = llm_router.run(prompt=prompt, task_type="analysis")

        if response["status"] == "error":
            raise HTTPException(status_code=500, detail=response["output"])

        return {"output": response["output"]}

    except HTTPException as http_exc:
        # Re-raise HTTPException to let FastAPI handle it
        raise http_exc
    except Exception as e:
        # Catch any other exceptions and return a generic 500 error
        return {"output": f"An unexpected error occurred: {e}"}
