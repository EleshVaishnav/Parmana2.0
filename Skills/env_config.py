from .registry import registry
import os

@registry.register(
    name="get_env_config",
    description="Reads a specific environment variable from the system.",
    parameters={
        "var_name": {"type": "string", "description": "The name of the environment variable (e.g., PATH)"}
    }
)
def get_env_config(var_name: str) -> str:
    # Blacklist sensitive keys naturally
    if "KEY" in var_name.upper() or "TOKEN" in var_name.upper():
         return "[Security] Cannot dump raw KEYS or TOKENS to the context window."
    val = os.environ.get(var_name, None)
    if val is None:
        return f"Variable {var_name} not found."
    return str(val)
