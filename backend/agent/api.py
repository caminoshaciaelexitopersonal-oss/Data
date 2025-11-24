from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

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
    message and the context from the current session, following the correct
    LangChain message structure.
    """
    try:
        df = state_store.load_dataframe(session_id=request.session_id)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for session_id: {request.session_id}. Please upload a file first.")

        # Construct the context as a SystemMessage
        context = f"""
        You are a data analysis assistant. Your task is to answer questions based on the following dataset.
        Provide clear, concise answers and do not make up information.

        Dataset context (first 5 rows in Markdown format):
        {df.head().to_markdown()}
        """

        system_message = SystemMessage(content=context)
        human_message = HumanMessage(content=request.message)

        # Pass the structured messages to the LLM router
        response = llm_router.run(prompt=[system_message, human_message], task_type="analysis")

        if response["status"] == "error":
            raise HTTPException(status_code=500, detail=response["output"])

        return {"output": response["output"]}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return {"output": f"An unexpected error occurred: {e}"}
