from .registry import registry
from datetime import datetime

@registry.register(
    name="task_planning",
    description="Creates a structured, logical plan broken down into steps before executing a complex task.",
    parameters={
        "objective": {"type": "string", "description": "The main goal to achieve."},
        "steps": {"type": "array", "items": {"type": "string"}, "description": "List of sequential steps"}
    }
)
def task_planning(objective: str, steps: list) -> str:
    plan = f"Task Plan for: {objective}\nCreated at: {datetime.now()}\n"
    for i, step in enumerate(steps):
        plan += f"{i+1}. {step}\n"
    return plan + "\nPlan has been registered and confirmed."
