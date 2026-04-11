from .registry import registry
import datetime

@registry.register(
    name="schedule_action",
    description="Schedules a conceptual action to occur at a specific future datetme.",
    parameters={
        "action_description": {"type": "string", "description": "What to do"},
        "time_str": {"type": "string", "description": "Time in YYYY-MM-DD HH:MM:SS format"}
    }
)
def schedule_action(action_description: str, time_str: str) -> str:
    try:
        dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return f"Successfully scheduled '{action_description}' for {dt}. Note: Background task runner required to actively execute."
    except Exception as e:
        return f"Schedule Error: {str(e)}"
