from fastapi import FastAPI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from backend.llm.llm_router import get_llm_for_agent
from backend.tools.main_tools import get_tools
from backend.app_factory import create_app

# --- Agent Setup ---
# This setup is now compatible with the langchain versions selected by pip-tools.
# We manually define a template compatible with the create_react_agent function.

template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

prompt = PromptTemplate.from_template(template)

# Create the agent
llm = get_llm_for_agent("analysis")
tools = get_tools()
agent = create_react_agent(llm, tools, prompt)

# Create the Agent Executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- App Creation ---
app = create_app()

# Attach the agent_executor to the app's state
app.state.agent_executor = agent_executor

@app.get("/")
def read_root():
    return {"message": "SADI Backend is running."}
