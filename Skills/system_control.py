import subprocess
from .registry import registry

@registry.register(
    name="execute_terminal_command",
    description="Executes a command on the user's terminal/PC. Use this to install packages, manipulate files, or control the system. CAUTION: This runs directly on the user's machine.",
    parameters={
        "command": {
            "type": "string",
            "description": "The terminal command to execute."
        }
    }
)
def execute_terminal_command(command: str) -> str:
    """Executes a terminal command and returns its output."""
    try:
        print(f"[Terminal] Executing: {command}")
        # Run command with shell=True to support shell builtins and pipes
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30 # 30 second timeout per command
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
            
        if not output.strip():
            return f"Command executed successfully (no output). Exit code: {result.returncode}"
            
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
