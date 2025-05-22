
from typing import Any, List, Dict
from google.adk.agents import Agent
from google.adk.tools import BaseTool
from config.config import MODEL
from ...session_utils import SessionUtils
from ...logger import logger
from .prompts import return_instructions_root
from .tools import vertex_search_tool


def create_rag_agent(
        model: Any = MODEL,
        name: str = "rag_agent",
        instruction: str = "",
        tools: List[BaseTool] = [],
        sub_agents: List[Agent] = []
        ) -> Agent:
    

    default_tools = [vertex_search_tool]

    default_sub_agents = []

    final_tools = SessionUtils.dedupe_lists(default_tools, tools)
    final_sub_agents = SessionUtils.dedupe_lists(default_sub_agents, sub_agents)

    
    logger.info("logger creating RAG agent")

    agent = Agent(
    name=name,
    model=MODEL,
    description=('RAG on provided data stores'),
    instruction=return_instructions_root(),
    sub_agents=final_sub_agents,
    tools=final_tools,
    )

    return agent
