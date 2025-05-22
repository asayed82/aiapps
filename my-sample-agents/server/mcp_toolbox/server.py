import subprocess
import os
import shlex
from google.adk.tools.toolbox_tool import ToolboxTool

MCP_TOOLBOX_EXECUTABLE = os.environ.get('MCP_TOOLBOX_EXECUTABLE', './toolbox')
MCP_TOOLBOX_YAML_PATH = os.environ.get('MCP_TOOLBOX_YAML_PATH', 'tools.yaml')
MCP_TOOLBOX_HOST = os.environ.get('MCP_TOOLBOX_HOST', '127.0.0.1')
MCP_TOOLBOX_PORT = os.environ.get('MCP_TOOLBOX_PORT', '5000')



# --- Constructing and Running the Command ---
def run_mcp_toolbox_server():
    """
    Constructs and runs the MCP toolbox server command.
    """
    
    # Check if the tools.yaml file exists if a specific path is given
    if not os.path.exists(MCP_TOOLBOX_YAML_PATH):
        print(f"Error: tools.yaml file not found at '{MCP_TOOLBOX_YAML_PATH}'")
        if MCP_TOOLBOX_YAML_PATH == 'tools.yaml':
            print("Consider setting the MCP_TOOLS_YAML_PATH environment variable.")
        return None

    # Check if the toolbox executable exists and is executable
    if not os.path.isfile(MCP_TOOLBOX_EXECUTABLE) or not os.access(MCP_TOOLBOX_EXECUTABLE, os.X_OK):
        print(f"Error: Toolbox executable not found or not executable at '{MCP_TOOLBOX_EXECUTABLE}'")
        if MCP_TOOLBOX_EXECUTABLE == './toolbox':
             print("Consider setting the MCP_TOOLBOX_EXECUTABLE environment variable to the full path.")
        return None

    command = [
        MCP_TOOLBOX_EXECUTABLE,
        '--tools-file', MCP_TOOLBOX_YAML_PATH,
        '--address', MCP_TOOLBOX_HOST,
        '--port', MCP_TOOLBOX_PORT
    ]

    print(f"Attempting to run MCP Toolbox server with command:")
    # Use shlex.join for a printable version of the command (Python 3.8+)
    # For older Python, you might just print the list: print(command)
    try:
        print(f"  {' '.join(shlex.quote(str(arg)) for arg in command)}")
    except AttributeError: # shlex.quote not available or for older shlex
        print(f"  {command}")


    try:
        
        process = subprocess.Popen(command)
        print(f"MCP Toolbox server started with PID: {process.pid}")
        print(f"Listening on {MCP_TOOLBOX_HOST}:{MCP_TOOLBOX_PORT}")
        
        return process # Return the process object if you need to manage it

    except FileNotFoundError:
        # This specific exception for the executable itself is less likely
        # if we do the os.path.isfile check above, but good to have.
        print(f"Error: The toolbox executable '{MCP_TOOLBOX_EXECUTABLE}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while trying to start the MCP Toolbox server: {e}")
        return None

if __name__ == '__main__':
    server_process = run_mcp_toolbox_server()

    if server_process:
        print("Server process object:", server_process)
        try:
            server_process.wait() # Wait for the process to terminate
            print(f"Server process {server_process.pid} has terminated with code {server_process.returncode}.")
        except KeyboardInterrupt:
            print(f"\nShutting down MCP Toolbox server (PID: {server_process.pid})...")
            server_process.terminate() # Send SIGTERM
            try:
                server_process.wait(timeout=5) # Wait a bit for graceful shutdown
            except subprocess.TimeoutExpired:
                print("Server did not terminate gracefully, sending SIGKILL.")
                server_process.kill() # Force kill
            print("Server shut down.")