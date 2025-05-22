from typing import Any, List
from google.adk.agents import Agent
from google.adk.tools import BaseTool
from config.config import MODEL
from .prompts import Prompts
from ...session_utils import SessionUtils
from ...logger import logger
from .tools import interview_db_toolset


def create_interview_agent(
        model: Any = MODEL,
        name: str = "hr_agent",
        global_instruction: str = Prompts.GLOBAL_PROMPT,
        instruction: str = Prompts.INTERVIEW_PROMPT,
        tools: List[BaseTool] = [],
        sub_agents: List[Agent] = []
        ) -> Agent:
    
    logger.info("logger creating agent")

    default_tools = [
    ]
    default_sub_agents = []

    final_tools = SessionUtils.dedupe_lists(default_tools, tools)
    final_tools = SessionUtils.dedupe_lists(final_tools, interview_db_toolset)
    final_sub_agents = SessionUtils.dedupe_lists(default_sub_agents, sub_agents)

    agent = Agent(
        model=model,
        name=name,
        global_instruction=global_instruction,
        instruction=instruction,
        tools=final_tools,
        sub_agents=final_sub_agents,
    )

    return agent