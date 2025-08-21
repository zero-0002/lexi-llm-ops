import subprocess
import logging
from mcp.server.fastmcp import FastMCP
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[92m%(asctime)s [%(levelname)s] %(message)s\033[0m"
)
# Create an MCP server
mcp = FastMCP("ShellOps")

@mcp.tool()
def execute_shell_command(command: str, time_limit: int) -> dict:
    """
    Execute a shell command and return the result.
    
    Args:
        command (str): The shell command to execute.
        time_limit (int): Maximum allowed execution time in seconds.
        
    Returns:
        dict: The result containing 'status', 'stdout', 'stderr', or 'message' in case of an error.
    """
    if not command:
        return {"status": "error", "message": "Command cannot be empty."}
    
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
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{command}' failed with return code {e.returncode}.")
        return {
            "status": "error",
            "message": f"Command '{command}' failed with return code {e.returncode}.",
            "stdout": e.stdout,
            "stderr": e.stderr
        }
    except Exception as e:
        logging.error(f"Unexpected error while executing command: {e}")
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}

if __name__ == "__main__":
    # Run the MCP server over stdio
    logging.info("MCP Server 'ShellOps' started over stdio")
    mcp.run(transport="stdio")
