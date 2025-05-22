from typing import Any, List, Dict
from google.adk.agents import Agent
from google.adk.tools import BaseTool

from config.config import MODEL
from ...session_utils import SessionUtils
from ...logger import logger

from google.adk.agents import Agent

from .prompts import Prompts
from .tools import call_critic_agent, call_reviser_agent
from ...session_utils import SessionUtils

from google.adk.agents import SequentialAgent
from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent



fact_checker_agent = SequentialAgent(
    name="fact_checker",
    description=(
        'Evaluates LLM-generated answers, verifies actual accuracy using the'
        ' web, and refines the response to ensure alignment with real-world knowledge.'
    ),
    sub_agents=[critic_agent, reviser_agent]
    
    )

def create_auditor_agent(
        model: Any = MODEL,
        name: str = "auditor_agent",
        instruction: str = Prompts.AUDITOR_PROMPT,
        tools: List[BaseTool] = [],
        sub_agents: List[Agent] = []
        ) -> Agent:
    

    default_tools = [call_critic_agent, call_reviser_agent]

    default_sub_agents = []

    final_tools = SessionUtils.dedupe_lists(default_tools, tools)
    final_sub_agents = SessionUtils.dedupe_lists(default_sub_agents, sub_agents)

    
    logger.info("logger creating auditor agent")

    agent = Agent(
    name=name,
    model=MODEL,
    description=(
        'Evaluates LLM-generated answers, verifies actual accuracy using the'
        ' web, and refines the response to ensure alignment with real-world knowledge.'
    ),
    instruction= Prompts.AUDITOR_PROMPT,
    tools=final_tools,
    sub_agents=final_sub_agents
    
    )

    return agent