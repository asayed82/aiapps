import os
from ...logger import logger
from google.adk.tools.toolbox_tool import ToolboxTool
from dotenv import load_dotenv

load_dotenv()

MCP_TOOLBOX_URL = os.environ.get('MCP_TOOLBOX_URL', 'http://127.0.0.1:5000')


toolbox = ToolboxTool(MCP_TOOLBOX_URL)
interview_db_toolset = toolbox.get_toolset(toolset_name='interview_db_toolset')
