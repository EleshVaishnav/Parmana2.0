from .registry import registry

@registry.register(
    name="chain_workflows",
    description="Constructs a workflow pipeline context.",
    parameters={
        "workflow_steps": {"type": "array", "items": {"type": "string"}, "description": "Ordered events"}
    }
)
def workflow_chaining(workflow_steps: list) -> str:
    chain = " -> ".join(workflow_steps)
    return f"Successfully established workflow chain: {chain}"
