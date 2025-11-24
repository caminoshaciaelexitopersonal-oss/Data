import pytest
import os
os.environ['TESTING'] = 'True'
from fastapi.testclient import TestClient
from backend.main import app

class DummyAgent:
    async def ainvoke(self, data, config=None):
        return {"output": f"Mocked agent response for session {config.get('configurable', {}).get('session_id', 'N/A')}."}

@pytest.fixture(scope="module")
def test_app():
    """
    Provides the FastAPI app instance for testing.
    The agent is now self-contained within the agent router and does not
    need to be mocked globally here. Specific tests can mock if needed.
    """
    return app

@pytest.fixture(scope="module")
def client(test_app):
    """
    Creates a TestClient for the FastAPI app.
    """
    with TestClient(test_app) as c:
        yield c
