import subprocess
import logging
from mcp.server.fastmcp import FastMCP
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agent.schemas import ToolOutputEnvelope

logging.basicConfig(
    level=logging.INFO,
    format="\033[92m%(asctime)s [%(levelname)s] %(message)s\033[0m"
)
# Create an MCP server
mcp = FastMCP("ShellOps")

@mcp.tool()
def execute_shell_command(command: str, time_limit: int) -> ToolOutputEnvelope:
    """
    Run a shell command inside the system environment with a maximum time limit.
    
    Args:
        command (str): The full shell command to be executed (e.g., "ls -l /tmp"). 
        time_limit (int): Maximum allowed execution time in seconds.
    Notes:
        - Use this tool when you need to directly inspect the system environment, 
          run diagnostic commands, or manipulate files via shell.  
    """
    if not command:
        return ToolOutputEnvelope(
            status="error",
            error_message="Command cannot be empty."
        )

    try:
        logging.info(f"COMMAND: Executing shell command: '{command}'")
        # logging.info("MCP Server 'ShellOps' started over stdio")
        result = subprocess.run(
            command,
            shell=True,          # Allow complex shell commands
            check=True,          # Raise error if command fails
            capture_output=True, # Capture output
            text=True,           # Return output as text
            timeout=time_limit   # Prevent command from running too long
        )
        return ToolOutputEnvelope(
            status="success",
            data={
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{command}' failed with return code {e.returncode}.")
        return ToolOutputEnvelope(
            status="error",
            error_message=f"Command '{command}' failed with return code {e.returncode}.",
            data={
                "stdout": e.stdout,
                "stderr": e.stderr
            }
        )
    except Exception as e:
        logging.error(f"Unexpected error while executing command: {e}")
        return ToolOutputEnvelope(
            status="error",
            error_message=f"An unexpected error occurred: {str(e)}"
        )

if __name__ == "__main__":
    # Run the MCP server over stdio
    logging.info("MCP Server 'ShellOps' started over stdio")
    mcp.run(transport="stdio")
