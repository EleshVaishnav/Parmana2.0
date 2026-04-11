from .registry import registry

@registry.register(
    name="debug_error",
    description="Analyzes an error message and suggests a fix.",
    parameters={
        "error_traceback": {"type": "string", "description": "The raw error output"},
        "context_info": {"type": "string", "description": "Any additional context"}
    }
)
def debug_error(error_traceback: str, context_info: str = "") -> str:
    return f"Debug Note: You must evaluate this traceback using your native LLM cognition.\nTraceback: {error_traceback}\nContext: {context_info}"
