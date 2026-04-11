from .registry import registry
import time

@registry.register(
    name="retry_failed_task",
    description="A logic tool that simulates an automatic retry loop for a failed task.",
    parameters={
        "task_name": {"type": "string", "description": "The task that failed"},
        "retry_count": {"type": "integer", "description": "How many times to retry"}
    }
)
def error_handling(task_name: str, retry_count: int) -> str:
    # Simulates error retry sleep logic
    time.sleep(1)
    return f"Automated retry circuit completed {retry_count} times for {task_name}."
