import pytest
import os
os.environ['TESTING'] = 'True'
from fastapi.testclient import TestClient
from backend.app_factory import create_app
from backend.celery_app import create_celery_app

@pytest.fixture(scope="session")
def celery_app_for_testing():
    """
    Creates a Celery app instance configured for testing (eager mode).
    This fixture is session-scoped to avoid re-creation for every test.
    """
    return create_celery_app(task_always_eager=True)

from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from backend.llm.llm_router import get_llm_for_agent
from backend.tools.main_tools import get_tools

class DummyAgent:
    async def ainvoke(self, data):
        return {"output": "Mocked agent response."}

@pytest.fixture(scope="module")
def test_app(celery_app_for_testing):
    """
    Creates a FastAPI app instance for testing, including the agent executor.
    """
    app = create_app()

    # Attach a dummy agent executor for testing
    app.state.agent_executor = DummyAgent()
    return app

@pytest.fixture(scope="module")
def client(test_app):
    """
    Creates a TestClient for the FastAPI app.
    """
    with TestClient(test_app) as c:
        yield c
