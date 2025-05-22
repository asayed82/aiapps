"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.base_tool import BaseTool 
from google.genai import types 
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator


from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent



class ReviserAgentTool(BaseTool):  # Create a class inheriting from BaseTool
    name: str = "reviser_agent_tool"
    description: str = "Reviser Agent tool."

    async def run_async(
        self,
        args: dict[str, object],
        tool_context: ToolContext,
    ) -> AsyncGenerator[types.Content, None]:  # Define _call_live method
        agent_tool = AgentTool(agent=reviser_agent)
        agent_output = await agent_tool.run_async(
            args=args, tool_context=tool_context
        )
        tool_context.state["agent_output"] = agent_output
        if agent_output:
            tool_context.state["query_result"] = agent_output
        yield types.Content(
            parts=[types.Part.from_text(text=agent_output)]
        )  # Yield the output as a Content object


async def call_reviser_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call reviser agent."""
    async for output in ReviserAgentTool(
        name="reviser_agent_tool", description="Agent use to revise fact."
    ).run_async(args={"request": question}, tool_context=tool_context):
        yield output


class CriticAgentTool(BaseTool):  # Create a class inheriting from BaseTool
    name: str = "critic_agent_tool"
    description: str = "Critic Agent tool."

    async def run_async(
        self,
        args: dict[str, object],
        tool_context: ToolContext,
    ) -> AsyncGenerator[types.Content, None]:  # Define _call_live method
        agent_tool = AgentTool(agent=critic_agent)
        agent_output = await agent_tool.run_async(
            args=args, tool_context=tool_context
        )
        tool_context.state["agent_output"] = agent_output
        if agent_output:
            tool_context.state["query_result"] = agent_output
        yield types.Content(
            parts=[types.Part.from_text(text=agent_output)]
        )  # Yield the output as a Content object


async def call_critic_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call critic agent."""
    async for output in CriticAgentTool(
        name="critic_agent_tool", description="Agent use to critic given facts"
    ).run_async(args={"request": question}, tool_context=tool_context):
        yield output

