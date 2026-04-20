from .registry import registry

@registry.register(
    name="register_trigger",
    description="Registers an event trigger in the framework.",
    parameters={
        "trigger_condition": {"type": "string", "description": "E.g., 'on_startup', 'on_error'"},
        "action": {"type": "string", "description": "The tool to trigger"}
    }
)
def event_triggers(trigger_condition: str, action: str) -> str:
    return f"Event hook registered: {action} will execute {trigger_condition}."
