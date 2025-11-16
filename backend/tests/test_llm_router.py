import pytest
from unittest.mock import patch, MagicMock
import os

from backend.llm import llm_router

# --- Fixtures y Mocks ---

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Fixture para simular la presencia de claves de API."""
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-google-key")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://fake-ollama:11434")

@pytest.fixture
def mock_llm_clients():
    """Fixture para mockear los clientes de LLM y sus respuestas."""
    with patch('backend.llm.llm_router._get_gemini_client') as mock_gemini, \
         patch('backend.llm.llm_router._get_openai_client') as mock_openai, \
         patch('backend.llm.llm_router._get_ollama_client') as mock_ollama:

        # Configurar mocks para que devuelvan un cliente mockeado
        mock_gemini.return_value = MagicMock()
        mock_gemini.return_value.invoke.return_value.content = "Respuesta de Gemini"

        mock_openai.return_value = MagicMock()
        mock_openai.return_value.invoke.return_value.content = "Respuesta de OpenAI"

        mock_ollama.return_value = MagicMock()
        mock_ollama.return_value.invoke.return_value = "Respuesta de Ollama" # Ollama no tiene .content

        yield {
            "gemini": mock_gemini,
            "openai": mock_openai,
            "ollama": mock_ollama
        }

# --- Pruebas para la Función `run` ---

def test_run_selects_by_preference(mock_llm_clients):
    """Verifica que la preferencia del modelo anula la selección por tarea."""
    response = llm_router.run("Test prompt", task_type="analysis", model_preference="openai")
    assert response["status"] == "ok"
    assert response["model_used"] == "gpt-4"
    assert response["output"] == "Respuesta de OpenAI"
    mock_llm_clients["openai"].return_value.invoke.assert_called_once()
    mock_llm_clients["ollama"].return_value.invoke.assert_not_called()

def test_run_selects_by_task(mock_llm_clients):
    """Verifica la selección de modelo basada en el tipo de tarea."""
    response = llm_router.run("Test prompt", task_type="writing") # 'writing' mapea a 'gemini'
    assert response["status"] == "ok"
    assert response["model_used"] == "gemini-pro"
    assert response["output"] == "Respuesta de Gemini"
    mock_llm_clients["gemini"].return_value.invoke.assert_called_once()

def test_run_fallback_mechanism(mock_llm_clients):
    """Prueba el mecanismo de fallback cuando el modelo preferido no está disponible."""
    # Simular que Gemini (preferido para 'writing') no está disponible
    mock_llm_clients["gemini"].return_value = None

    response = llm_router.run("Test prompt", task_type="writing")

    # Debería hacer fallback a Ollama
    assert response["status"] == "ok"
    assert response["model_used"] == "ollama-llama3"
    assert response["output"] == "Respuesta de Ollama"
    mock_llm_clients["ollama"].return_value.invoke.assert_called_once()

def test_run_no_clients_available(mock_llm_clients):
    """Prueba el caso en que ningún cliente de LLM está disponible."""
    mock_llm_clients["gemini"].return_value = None
    mock_llm_clients["openai"].return_value = None
    mock_llm_clients["ollama"].return_value = None

    response = llm_router.run("Test prompt")

    assert response["status"] == "error"
    assert "No LLM clients are available" in response["output"]

def test_standardized_output_format(mock_llm_clients):
    """Verifica que la salida siempre sigue el formato estándar."""
    response = llm_router.run("Test prompt", model_preference="gemini")
    assert "status" in response
    assert "model_used" in response
    assert "output" in response
    assert "tokens" in response

# --- Pruebas para la Función `get_llm_for_agent` ---

def test_get_llm_for_agent_preference(mock_llm_clients):
    """Prueba que `get_llm_for_agent` respeta la preferencia."""
    llm_instance = llm_router.get_llm_for_agent(model_preference="openai")
    assert llm_instance == mock_llm_clients["openai"].return_value
    mock_llm_clients["openai"].assert_called_once()
    mock_llm_clients["gemini"].assert_not_called()

def test_get_llm_for_agent_fallback(mock_llm_clients):
    """Prueba el fallback de `get_llm_for_agent`."""
    # Simular que el preferido (OpenAI) no está disponible
    mock_llm_clients["openai"].return_value = None

    llm_instance = llm_router.get_llm_for_agent(model_preference="openai")

    # Debería hacer fallback (el primero es Ollama)
    assert llm_instance == mock_llm_clients["ollama"].return_value
    mock_llm_clients["ollama"].assert_called_once()

def test_get_llm_for_agent_raises_error_if_none_available(mock_llm_clients):
    """Prueba que `get_llm_for_agent` lanza una excepción si ningún cliente funciona."""
    mock_llm_clients["gemini"].return_value = None
    mock_llm_clients["openai"].return_value = None
    mock_llm_clients["ollama"].return_value = None

    with pytest.raises(RuntimeError, match="Fatal: No LLM clients could be initialized."):
        llm_router.get_llm_for_agent()
