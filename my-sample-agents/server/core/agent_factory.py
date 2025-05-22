from config.config import DEMO_TYPE
from core.agents.hr.hr_agent import create_interview_agent
from core.agents.llm_auditor.agent import create_auditor_agent
from core.agents.rag.agent import create_rag_agent
from core.agents.hr.context import AgentContext

from .logger import logger

def get_agent_config():

    agent_config = {"app_name": "NA", "root_agent": None, "context": None}

    if DEMO_TYPE == "hr":
        agent_config["app_name"] = "hr_assist"
        agent_config["context"] = AgentContext.INTERVIEW_CONTEXT
        agent_config["root_agent"] = create_interview_agent()

    elif DEMO_TYPE == "auditor":
        agent_config["app_name"] = "llm_auditor"
        agent_config["context"] = AgentContext.AUDITOR_CONTEXT
        agent_config["root_agent"] = create_auditor_agent()

    elif DEMO_TYPE == "rag":
        agent_config["app_name"] = "rag"
        agent_config["context"] = AgentContext.RAG_CONTEXT
        agent_config["root_agent"] = create_rag_agent()
    else:
        raise ValueError(f"Unknown DEMO_TYPE: `{DEMO_TYPE}`")

    return agent_config
