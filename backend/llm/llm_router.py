import os
import logging
from typing import Dict, Any, Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load API keys and base URLs securely from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")

# --- Model Clients ---
def _get_gemini_client() -> ChatGoogleGenerativeAI:
    """Initializes and returns the Gemini client if the API key is available."""
    if not GOOGLE_API_KEY:
        return None
    # Forcing the standard, most common model name after dependency updates.
    return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0, google_api_key=GOOGLE_API_KEY)

def _get_openai_client() -> ChatOpenAI:
    """Initializes and returns the OpenAI client if the API key is available."""
    if not OPENAI_API_KEY:
        return None
    return ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4", temperature=0)

def _get_ollama_client(model: str = "llama3") -> Ollama:
    """Initializes and returns the Ollama client only if OLLAMA_BASE_URL is set."""
    if not OLLAMA_BASE_URL:
        return None
    # Note: This assumes the Ollama service is reachable.
    # A real implementation should have a health check.
    return Ollama(base_url=OLLAMA_BASE_URL, model=model, temperature=0)

# --- Task-Based Model Selection ---
TASK_TO_MODEL_MAP = {
    'analysis': 'ollama',
    'writing': 'gemini',
    'semantic_check': 'gemini',
    'summary': 'openai',
}

def _select_model_by_task(task_type: str) -> str:
    """Selects the best model provider based on the task type."""
    return TASK_TO_MODEL_MAP.get(task_type.lower(), 'gemini') # Default to Gemini

# --- Main Router Logic ---
def run(
    prompt: list,  # Now expects a list of LangChain messages
    task_type: str = "analysis",
    model_preference: str = None
) -> Dict[str, Any]:
    """
    Selects and runs the appropriate LLM based on task, preference, and availability.

    :param prompt: The input prompt for the LLM, as a list of LangChain messages.
    :param task_type: The type of task (e.g., 'analysis', 'writing').
    :param model_preference: A user-specified model preference ('gemini', 'openai', 'ollama').
    :return: A standardized dictionary with the LLM's response.
    """
    model_name = ""
    client = None

    # Determine the target model
    if model_preference:
        target_model = model_preference
    else:
        target_model = _select_model_by_task(task_type)

    # Attempt to get the client for the target model
    if target_model == "gemini":
        client = _get_gemini_client()
        model_name = "gemini-pro"
    elif target_model == "openai":
        client = _get_openai_client()
        model_name = "gpt-4"
    elif target_model == "ollama":
        client = _get_ollama_client()
        model_name = "ollama-llama3"

    # Fallback logic if the preferred client is not available
    if not client:
        logging.warning(f"Client for preferred model '{target_model}' not available. Attempting fallback.")
        # Try Ollama first as it's local, then Gemini, then OpenAI
        client = _get_ollama_client()
        model_name = "ollama-llama3"
        if not client:
            client = _get_gemini_client()
            model_name = "gemini-pro"
            if not client:
                client = _get_openai_client()
                model_name = "gpt-4"

    # If no client is available after all fallbacks, return an error
    if not client:
        return {
            "status": "error",
            "model_used": "none",
            "output": "No LLM clients are available. Please check API keys and service availability.",
            "tokens": {}
        }

    # Invoke the model and return the standardized response
    try:
        response = client.invoke(prompt)
        output_text = response.content if hasattr(response, 'content') else str(response)

        # Token usage can vary between models, so we access it safely
        token_usage = {}
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            token_usage = response.response_metadata['token_usage']

        return {
            "status": "ok",
            "model_used": model_name,
            "output": output_text,
            "tokens": token_usage
        }
    except Exception as e:
        logging.error(f"An error occurred while invoking model {model_name}: {e}")
        return {
            "status": "error",
            "model_used": model_name,
            "output": f"An error occurred: {e}",
            "tokens": {}
        }

# --- Agent Integration Utility ---
def get_llm_for_agent(model_preference: str = "gemini"):
    """
    Returns a compatible LLM instance for a LangChain agent.
    This is kept for compatibility with the current agent setup.
    """
    client = None
    if model_preference == "openai":
        client = _get_openai_client()
    elif model_preference == "ollama":
        client = _get_ollama_client()
    else: # Default to Gemini
        client = _get_gemini_client()

    # If the preferred client failed (e.g., missing key), fallback gracefully
    if not client:
        logging.warning(f"Could not initialize preferred model '{model_preference}'. Falling back.")
        client = _get_ollama_client() or _get_gemini_client() or _get_openai_client()

    if not client:
        raise RuntimeError("Fatal: No LLM clients could be initialized.")

    return client
