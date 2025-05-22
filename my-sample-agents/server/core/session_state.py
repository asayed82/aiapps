
from typing import Any, Dict, Optional
from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from config.config import CONFIG
from .logger import logger

class SessionState:
    """
    Represents the state of a user/agent session, encapsulating the agent, services, and context.

    This class manages the lifecycle of a user/agent session, including agent setup,
    service initialization, context management, and tracking of session events.
    It provides methods to access and initialize session services and artifact services,
    and to manage the runner and live request queue.

    Attributes:
        agent (Agent): The agent associated with the session.
        app_name (str): The name of the application associated with the session.
        user_id (str): The unique user identifier for the session.
        session_service_type (str): The type of session service to use (e.g., "in_memory").
        artifact_service_type (str): The type of artifact service to use (e.g., "in_memory").
        session_service (Optional[Any]): The initialized session service object.
        artifact_service (Optional[Any]): The initialized artifact service object.
        session (Optional[Any]): The session object created by the session service.
        context (Optional[Dict[str, Any]]): The session context data.
        num_agents (int): The number of agents involved in the session.
        num_agents_set (bool): Flag indicating if the number of agents has been determined.
        runner (Runner): The runner object for executing the agent.
        live_request_queue (LiveRequestQueue): The queue for handling live requests.
        events (Optional[Any]): The event generator for the session.
        is_receiving_response (bool): Flag indicating if the session is currently receiving a response.
        interrupted (bool): Flag indicating if the session has been interrupted.
        current_audio_stream (Optional[Any]): The current audio stream object (if any).
        received_model_response (bool): Flag indicating if a model response has been received in the current turn.
    """
    def __init__(
            self,
            agent: Agent,
            app_name: str = "agent app",
            user_id: str = "userX",
            session_service: str = "in_memory",
            artifact_service: str = "in_memory",
            context: Dict[str, Any] = None,
            ):
        self.agent = agent
        self.app_name = app_name
        self.user_id = user_id
        self.session_service_type = session_service
        self.artifact_service_type = artifact_service
        self.session_service = None
        self.artifact_service = None
        self.session = None
        self.context = context
        self.num_agents = 1
        self.num_agents_set = False
        self.runner = self.setup()
        self.live_request_queue = LiveRequestQueue()
        self.events = None

        self.is_receiving_response: bool = False
        self.interrupted: bool = False
        #self.current_tool_execution: Optional[asyncio.Task] = None
        self.current_audio_stream: Optional[Any] = None
        #genai_session: Optional[Any] = None
        self.received_model_response: bool = False  # Track if we've received a model response in current turn

    def _get_session_service(self):
        """
        Retrieves or initializes the session service.

        Returns:
            Any: The initialized session service object.

        Raises:
            ValueError: If an unknown session service type is specified.
        """
        if self.session_service is None:
            if self.session_service_type == "in_memory":
                self.session_service = InMemorySessionService()
            else:
                raise ValueError(f"Unknown session_service: {self.session_service_type}")
        return self.session_service

    def _get_artifact_service(self):
        """
        Retrieves or initializes the artifact service.

        Returns:
            Any: The initialized artifact service object.

        Raises:
            ValueError: If an unknown artifact service type is specified.
        """
        if self.artifact_service is None:
            if self.artifact_service_type == "in_memory":
                self.artifact_service = InMemoryArtifactService()
            else:
                raise ValueError(f"Unknown artifact_service: {self.artifact_service_type}")
        return self.artifact_service

    def _set_num_agents_for_session(self, agent: Agent):
        """
        Determines the number of agents involved in the session.

        Args:
            agent (Agent): The root agent for the session.
        """
        if not self.num_agents_set:
            self.num_agents = 1 + len(agent.sub_agents)

    def log_event_output(self, event: Event):

        try:
            res = event.content.model_dump(exclude_none=True).get("parts", None)
        except Exception as e:
            logger.debug(f"e:{e}\nevent:{event}")
            return None

        if not res:
            return None

        for part in res:
            if part.get("text", None):
                if event.content.role == "model":
                    logger.info(f"{event.author}: {part['text']}")
                elif event.content.role == "user":
                    logger.info(f"USER QUERY: {part['text']}")

            if part.get("function_call", None):
                logger.info(f"TOOL CALL: {part['function_call']}")

            if part.get("function_response", None):
                logger.info(f"TOOL RESULT: {part['function_response']}")

        return res
            
    def setup(self):
        """
        Sets up the session, runner, and services.

        This method initializes the session service, artifact service, and runner,
        and creates a new session if one does not already exist.

        Returns:
            Runner: The initialized runner object.
        """
        self._set_num_agents_for_session(self.agent)
        session_service = self._get_session_service()
        artifact_service = self._get_artifact_service()

        if not self.session:
            if self.context:
                print("INFO: Creating new session with session context")
                self.session = session_service.create_session(
                    app_name=self.app_name,
                    user_id=self.user_id,
                    state=self.context)
            else:
                print("INFO: Creating new session with no context")
                self.session = session_service.create_session(
                    app_name=self.app_name,
                    user_id=self.user_id,)

        return Runner(
            app_name=self.app_name,
            agent=self.agent,
            artifact_service=self.artifact_service,
            session_service=self.session_service,
            #response_modalities=CONFIG["generation_config"]["response_modalities"]
        )