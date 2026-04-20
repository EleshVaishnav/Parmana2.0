from .registry import registry

@registry.register(
    name="system_notify",
    description="Sends a desktop or system-wide OS notification flag.",
    parameters={
        "title": {"type": "string", "description": "Notification title"},
        "text": {"type": "string", "description": "Notification text"}
    }
)
def notifications(title: str, text: str) -> str:
    # Stub for OS-level notify library (win10toast or pync)
    return f"OS Notification Triggered: [{title}] {text}"
