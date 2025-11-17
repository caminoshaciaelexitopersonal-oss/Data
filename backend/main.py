import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app_factory import create_app
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from backend.llm.llm_router import get_llm_for_agent
from backend.tools.main_tools import get_tools

# Get the ReAct agent prompt
prompt = hub.pull("hwchase17/react")

# Create the agent
# Note: In a real app, the LLM might be selected based on the request
llm = get_llm_for_agent("analysis") # Default LLM
tools = get_tools()
agent = create_react_agent(llm, tools, prompt)

# Create the Agent Executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Create the FastAPI app
app = create_app()

# Attach the agent_executor to the app's state so it can be accessed in routers
app.state.agent_executor = agent_executor

@app.get("/")
def read_root():
    return {"message": "SADI Backend is running."}
