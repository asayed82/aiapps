"""
WebSocket message handling from the client/frontend to proxy and from proxy to the live Agent
"""
import json
import asyncio
import sys
import base64
import traceback
from typing import Any, Optional
from google.genai import types
from typing import Dict, Any, Optional
from google.adk.agents.run_config import RunConfig

from google.adk.agents import Agent

from core.agent_factory import get_agent_config
from .session_state import SessionState
from .logger import logger
from config.config import CONFIG

# Global session storage
ACTIVE_SESSIONS: Dict[str, SessionState] = {}

# TODO: Move Session CRUD ops to another file
def create_session(
        session_id: str,
        agent: Agent,
        app_name: str,
        context: Dict[str, Any]) -> SessionState:
    """
    Creates and stores a new session.

    This function initializes a new SessionState object with the provided agent,
    application name, and session ID. It then starts the agent's live runner and
    stores the session in the active sessions dictionary.

    Args:
        session_id: The unique identifier for the session.
        agent: The Agent object associated with the session.
        app_name: The name of the application associated with the session.

    Returns:
        SessionState: The newly created SessionState object.
    """
    session = SessionState(
        agent = agent,
        app_name = app_name,
        user_id = session_id,
        context = context)

    logger.info(f"Voice: {CONFIG["generation_config"]["speech_config"]}")
    logger.info(f"modalities: {CONFIG["generation_config"]["response_modalities"]}")

    run_config = RunConfig(
        response_modalities=CONFIG["generation_config"]["response_modalities"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfigDict(
                {"prebuilt_voice_config": {"voice_name": CONFIG["generation_config"]["speech_config"]}}
                ),
            language_code=CONFIG["generation_config"]["language_code"]
            ),
        output_audio_transcription=types.AudioTranscriptionConfig()
        )
    
    session.events = session.runner.run_live(
        session=session.session, 
        live_request_queue=session.live_request_queue,
        run_config=run_config,
        )

    ACTIVE_SESSIONS[session_id] = session
    return session

def get_session(session_id: str) -> Optional[SessionState]:
    """
    Retrieves an existing session from the active sessions dictionary.

    This function attempts to retrieve a session with the given session ID from
    the `active_sessions` dictionary. If a session with the specified ID exists,
    it is returned; otherwise, None is returned.

    Args:
        session_id: The unique identifier of the session to retrieve.

    Returns:
        Optional[SessionState]: The SessionState object if found, or None if not found.
    """
    return ACTIVE_SESSIONS.get(session_id)

def remove_session(session_id: str) -> None:
    """
    Removes a session from the active sessions dictionary.

    This function checks if a session with the given session ID exists in the
    `active_sessions` dictionary. If it exists, the session is removed.

    Args:
        session_id: The unique identifier of the session to remove.
    """
    if session_id in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[session_id] 


async def send_error_message(websocket: Any, error_data: dict) -> None:
    """
    Sends a formatted error message to the client via the websocket connection.

    This function constructs a JSON message containing the error type and data,
    and then attempts to send it through the provided websocket. If an error occurs
    during the sending process, it logs the error.

    Args:
        websocket: The websocket connection object used to send the error message.
        error_data: A dictionary containing the error details.

    Raises:
        Exception: If an error occurs during the websocket send operation.
    """
    try:
        await websocket.send(json.dumps({
            "type": "error",
            "data": error_data
        }))
    except Exception as e:
        logger.error(f"Failed to send error message: {e}")


# TODO - Update the cleanup to close the session of the agent
async def cleanup_session(session: Optional[SessionState], session_id: str) -> None:
    """
    Cleans up session resources, including closing the agent session and removing it from active sessions.

    This function performs the following actions:
    1. Checks if a session object exists.
    2. If the session exists, attempts to close the agent's session.
    3. Removes the session from the active sessions dictionary.
    4. Logs the successful cleanup of the session.

    Args:
        session: The SessionState object representing the session to be cleaned up.
        session_id: The unique identifier of the session.

    Raises:
        Exception: If an error occurs during the session cleanup process, such as closing the agent session.
    """
    try:
        if session:
            # Close agent session
            if session.session:
                try:
                    #print("TODO - Stop agent session")
                    session.live_request_queue.close() # TODO - makes sure that AF close fucntionality works
                    #await session.session.delete() # TODO - is the any close function in agent run_live?
                except Exception as e:
                    logger.error(f"Error closing Agent session: {e}")
            
            # Remove session from active sessions
            remove_session(session_id)
            logger.info(f"Session {session_id} cleaned up and ended")
    except Exception as cleanup_error:
        logger.error(f"Error during session cleanup: {cleanup_error}")

async def handle_agent_responses(websocket: Any, session: SessionState) -> None:
    """
    Handles responses from the agent, forwarding audio data to the client/frontend via websocket.

    This function iterates through the events generated by the agent's session, specifically
    looking for audio data. When audio data is found, it is base64 encoded and sent to the
    client through the provided websocket connection.

    Args:
        websocket: The websocket connection object used to send data to the client.
        session: The SessionState object containing the agent's session and events.

    Raises:
        Exception: If an error occurs during event processing or websocket communication.
    """
    try:
        full_text = ""
        async for event in session.events:
            event_index = len(session.session.events) - 1

            # --- Interruption ---
            if event.interrupted:
                #session.log_event_output("Interrupted event detected")
                logger.info("Interrupted event detected")

                await websocket.send(json.dumps({
                    "type": "interrupted",
                    "data": {
                        "message": "Response interrupted by user input"
                    }
                }))
                continue

            if event.content == None:
                logger.info(f"None content - turn_complete:{event.turn_complete}")
                continue

            # --- Tool Call and Result handling ---
            if event.content.parts[0].function_call:
                tool = event.content.parts[0].function_call
                tool_name = tool.name
                tool_args = tool.args
                await websocket.send(json.dumps({
                    "type": "tool_call",
                    "data": {"name": tool_name, "args": tool_args}
                }))
            elif event.content.parts[0].function_response:
                tool_result = event.content.parts[0].function_response
                tool_name = tool_result.name
                tool_output = tool_result.response
                await websocket.send(json.dumps({
                    "type": "tool_result",
                    "data": tool_output
                }))

            # --- Text and Markdown handling ---
            if event.content and event.content.parts and event.content.parts[0].text:
                full_text = event.content.parts[0].text 

                if not event.partial:
                    if full_text:
                        await websocket.send(json.dumps({
                            "type": "text",
                            "data": full_text
                        }))
                    full_text = ""

                #TODO - if you need to use Chrip voices, I suggest to use event.partial == True and play this text
            
            # --- Image handling ---
            inline_data = (
                event.content
                and event.content.parts
                and event.content.parts[0].inline_data
            )

            if inline_data and inline_data.mime_type.startswith('image'):
                image_base64 = base64.b64encode(inline_data.data).decode('utf-8')
                await websocket.send(json.dumps({
                    "type": "image",
                    "data": f"data:{inline_data.mime_type};base64,{image_base64}"
                }))
                continue

            # --- Audio handling ---
            inline_data = (
                event.content
                and event.content.parts
                and event.content.parts[0].inline_data
            )

            if inline_data and inline_data.mime_type.startswith('audio/pcm'):
                audio_base64 = base64.b64encode(inline_data.data).decode('utf-8')
                await websocket.send(json.dumps({
                    "type": "audio",
                    "data": audio_base64
                }))
                continue
            await asyncio.sleep(0)
    except Exception as e:
        logger.error(f"Error handling Gemini response: {e}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")

async def handle_client_messages(websocket: Any, session: SessionState) -> None:
    """
    Handles incoming messages from the client/frontend, processing audio, image, and text data.

    This function listens for messages on the provided websocket, parses them as JSON,
    and forwards the data to the agent's live request queue of the agent based on the message type.
    It supports 'audio', 'image', 'text', and 'end' message types.

    Args:
        websocket: The websocket connection object.
        session: The SessionState object containing the agent and request queue.

    Raises:
        Exception: If an error occurs during message processing or if the websocket connection is closed unexpectedly.
    """
    try:
        async for message in websocket:
            try:

                data = json.loads(message)
                # Handle different types of input
                if "type" in data:
                    msg_type = data["type"]
                    if msg_type == "audio":
                        logger.debug("Client -> Gemini: Sending audio data...")
                        ## Sending audio to the Agent
                        session.live_request_queue.send_realtime(
                                    types.Blob(data=data.get("data"), 
                                               mime_type='audio/pcm'))

                        logger.debug("Audio sent to Gemini")
                    elif msg_type == "image":
                        logger.debug("Client -> Gemini: Sending image data...")

                        ## Sending video/images to the Agent 
                        session.live_request_queue.send_realtime(
                                    types.Blob(data=data.get("data"), 
                                               mime_type='image/jpeg'))

                        logger.debug("Image sent to Gemini")
                    elif msg_type == "text":
                        logger.info("Sending text to Gemini...")
                        ## Sending text to the Agent 
                        session.live_request_queue.send_content(types.Content(
                                role='user', parts=[types.Part.from_text(text=data.get("data"))]))

                        logger.info("Text sent to Gemini")
                    elif msg_type == "end":
                        logger.info("Received end signal")
                    else:
                        debug_data = data.copy()
                        if "data" in debug_data and debug_data["type"] == "audio":
                            debug_data["data"] = "<audio data>"
                        logger.warning(f"Unsupported message type: {data.get('type')}")

            except Exception as e:
                logger.error(f"Error handling client message: {e}")
                logger.error(f"Full traceback:\n{traceback.format_exc()}")
    except Exception as e:
        if "connection closed" not in str(e).lower():  # Don't log normal connection closes
            logger.error(f"WebSocket connection error: {e}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise  # Re-raise to let the parent handle cleanup

# handle_messages  function creates the handlers for both client/frontend/webui and backend (handle_client_messages), and agent and backend (handle_agent_responses)
async def handle_messages(websocket: Any, session: SessionState) -> None:
    """Handles bidirectional message flow between client and Gemini."""
    client_task = None
    gemini_task = None

    try:
        async for message in websocket:
            logger.info(f"message from handle_messages={message}")
            try:
                async with asyncio.TaskGroup() as tg:
                    sys.stderr.write(f"tg =  {tg}.\n")
                    # Task 1: Handle incoming messages from client
                    client_task = tg.create_task(handle_client_messages(websocket, session))   # here we get the client messages
                    # Task 2: Handle responses from Gemini
                    gemini_task = tg.create_task(handle_agent_responses(websocket, session))  # here we need to replace it with agent framework
            except Exception as eg:
                logger.error(f"ExceptionGroup caught in TaskGroup eg =  {eg}.\n")
                handled = False
                for exc in eg.exceptions:
                    if "Quota exceeded" in str(exc):
                        logger.info("Quota exceeded error occurred")
                        try:
                            # Send error message for UI handling
                            await send_error_message(websocket, {
                                "message": "Quota exceeded.",
                                "action": "Please wait a moment and try again in a few minutes.",
                                "error_type": "quota_exceeded"
                            })
                            # Send text message to show in chat
                            await websocket.send(json.dumps({
                                "type": "text",
                                "data": "⚠️ Quota exceeded. Please wait a moment and try again in a few minutes."
                            }))
                            handled = True
                            break
                        except Exception as send_err:
                            logger.error(f"Failed to send quota error message: {send_err}")
                    elif "connection closed" in str(exc).lower():
                        logger.info("WebSocket connection closed")
                        handled = True
                        break
                
                if not handled:
                    # For other errors, log and re-raise
                    logger.error(f"Error in message handling: {eg}")
                    logger.error(f"Full traceback:\n{traceback.format_exc()}")
                    raise
            finally:
                # Cancel tasks if they're still running
                logger.info("Finally block for a message iteration.")
                if client_task and not client_task.done():
                    client_task.cancel()
                    try:
                        await client_task
                    except asyncio.CancelledError:
                        pass
                
                if gemini_task and not gemini_task.done():
                    gemini_task.cancel()
                    try:
                        await gemini_task
                    except asyncio.CancelledError:
                        pass
    except Exception as e:
        logger.error(f"Error in message handling: {e}")

    finally:
        logger.info("Exiting handle_messages function.")


async def handle_client(websocket: Any) -> None:
    """
    Handles a new client/frontend connection, initiating a session with a "talkative" root agent.

    This function performs the following steps:
    1. Generates a unique session ID based on the websocket object.
    2. Creates a root agent with predefined model, instructions, and settings.
    3. Establishes a new session using the created agent.
    4. Sends a "ready" message to the client/frontend indicating the session is active.
    5. Starts handling incoming messages from the client/frontend through the 'handle_messages' function.
    6. Gracefully handles potential errors, including connection closures, timeouts, and unexpected exceptions.
    7. Ensures proper session cleanup regardless of the outcome.

    Args:
        websocket: The websocket connection object representing the client/frontend.

    Raises:
        Exception: If an unexpected error occurs during message handling or other operations.
    """
    # """Handles a new client connection."""

    logger.info(f"we are in handle_client")

    session_id = str(id(websocket))

    agent_config = get_agent_config()
    app_name = agent_config.get("app_name")
    root_agent = agent_config.get("root_agent")
    context = agent_config.get("context")
    
    session = create_session(session_id, root_agent, app_name, context=context)

    try:
        # Send ready message to client
        await websocket.send(json.dumps({"ready": True}))
        logger.info(f"New session started: {session_id}")
        
        try:
            # Start message handling
            await handle_messages(websocket, session) # Here is the magic
        except Exception as e:
            if "code = 1006" in str(e) or "connection closed abnormally" in str(e).lower():
                logger.info(f"Browser disconnected or refreshed for session {session_id}")
                await send_error_message(websocket, {
                        "message": "Connection closed unexpectedly",
                        "action": "Reconnecting...",
                        "error_type": "connection_closed"
                })
            else:
                raise
            
    except asyncio.TimeoutError:
        logger.info(f"Session {session_id} timed out - this is normal for long idle periods")
        await send_error_message(websocket, {
            "message": "Session timed out due to inactivity.",
            "action": "You can start a new conversation.",
            "error_type": "timeout"
        })
    except Exception as e:
        logger.error(f"Error in handle_client: {e}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
        if "connection closed" in str(e).lower() or "websocket" in str(e).lower():
            logger.info(f"WebSocket connection closed for session {session_id}")
            # No need to send error message as connection is already closed
        else:
            await send_error_message(websocket, {
                "message": "An unexpected error occurred.",
                "action": "Please try again.",
                "error_type": "general"
            })
    finally:
        # Always ensure cleanup happens
        await cleanup_session(session, session_id) 