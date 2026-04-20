from .registry import registry
import subprocess

@registry.register(
    name="git_command",
    description="Executes a git command in the current repository.",
    parameters={
        "command": {"type": "string", "description": "The git command (e.g., 'status', 'log -n 3')"}
    }
)
def git_command(command: str) -> str:
    try:
        # Prevent dangerous stuff naturally by passing args
        full_command = f"git {command}"
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"Git Error: {str(e)}"
