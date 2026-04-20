from .registry import registry

@registry.register(
    name="reflect_tool_calling",
    description="A meta-cognitive tool that allows the LLM to inspect how a previous tool call was executed.",
    parameters={
        "tool_name": {"type": "string", "description": "Name of the tool"},
        "result_status": {"type": "string", "description": "How the execution went."}
    }
)
def tool_calling(tool_name: str, result_status: str) -> str:
    return f"Reflection noted for {tool_name}. Status: {result_status}"
