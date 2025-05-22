"""A set of utility methods that help manipulate Session context."""

from typing import Any, List, Dict
from google.genai import types

from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event, EventActions
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from .logger import logger

class SessionUtils:
    """A set of utility methods that help manipulate Session context."""

    @staticmethod
    def log_after_agent():
        logger.info("AFTER AGENT")

    @staticmethod
    def log_before_agent():
        logger.info("BEFORE AGENT")

    @staticmethod
    def log_before_tool():
        logger.info("BEFORE TOOL")

    @staticmethod
    def log_after_tool():
        logger.info("AFTER TOOL")

    @staticmethod
    def log_before_model():
        logger.info("BEFORE MODEL")

    @staticmethod
    def log_after_model():
        logger.info("AFTER MODEL")

    @staticmethod
    def build_content(content) -> types.Content:
        """
        Builds a types.Content object. (Same as before)
        """
        if isinstance(content, str):
            return types.Content(role="model", parts=[types.Part(text=content)])
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
        
        # TODO: Add other content types
        
    @staticmethod
    def get_state(
        context: CallbackContext | ToolContext | InvocationContext
        ) -> Dict[str, Any]:
        """Get the current state based on provided context."""
        if isinstance(context, CallbackContext):
            return context._invocation_context.session.state

        elif isinstance(context, ToolContext):
            return context._invocation_context.session.state
        
        elif isinstance(context, InvocationContext):
            return context.session.state

        else:
            raise ValueError(f"Unknown context type: {type(context)}")

    @staticmethod
    def update_state(
        context: CallbackContext | ToolContext | InvocationContext,
        data: Dict[str, Any]) -> None:
        """Update all k/v pairs in data back into session state."""
        if isinstance(context, InvocationContext):
            for k, v in data.items():
                context.session.state[k] = v

        elif isinstance(context, CallbackContext):
            for k, v in data.items():
                context._invocation_context.session.state[k] = v

        elif isinstance(context, ToolContext):
            for k, v in data.items():
                context._invocation_context.session.state[k] = v

        else:
            raise ValueError(f"Unknown context type: {type(context)}")

    @staticmethod
    def dedupe_lists(existing_list: List[Any], new_list: List[Any]):
        """Dedupe items from list."""
        final_list = []
        if new_list is None:
            final_list = existing_list
        else:
            final_list = existing_list + [
                item for item in new_list if item not in existing_list
                ]
        
        return final_list


    def model_response(
            self, text: str = None, function_call: types.FunctionCall = None,
            function_response: types.FunctionResponse = None):
        """Method to simplify creating agent response object."""

        ROLE = "model"
        if text:
            return types.Content(role=ROLE, parts=[types.Part.from_text(text=text)])
        elif function_call:
            return types.Content(role=ROLE, parts=[types.Part.from_function_call(function_call)])
        elif function_response:
            return types.Content(role=ROLE, parts=[function_response])
        else:
            raise ValueError("Either text or function_call must be provided")

    def build_event(
            self,
            context: InvocationContext | CallbackContext | ToolContext,
            text: str = None,
            function_call: types.FunctionCall = None,
            event_options: Dict[str, Any] = None) -> Event:
        """Method to simplify Event response object."""

        event_options_obj = EventActions(**event_options) if event_options else None

        if isinstance(context, InvocationContext):
            invocation_id = context.invocation_id
            author = context.agent.name

        elif isinstance(context, CallbackContext):
            invocation_id = context._invocation_context.invocation_id
            author = context._invocation_context.agent.name

        elif isinstance(context, ToolContext):
            invocation_id = context._invocation_context.invocation_id
            author = context._invocation_context.agent.name

        if event_options_obj:
            return Event(
                invocation_id=invocation_id,
                author=author,
                content=self.model_response(
                    text=text, function_call=function_call),
                options=event_options_obj
            )
        else:
            return Event(
                invocation_id=invocation_id,
                author=author,
                content=self.model_response(
                    text=text, function_call=function_call)
                )

