import inspect
from typing import Callable, Dict, Any, List

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: List[Dict[str, Any]] = []

    def register(self, name: str, description: str, parameters: Dict[str, Any], required: list = None):
        """Decorator to register a tool function."""
        def decorator(func: Callable):
            self.tools[name] = func
            req = required if required is not None else list(parameters.keys())
            self.schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": parameters,
                        "required": req
                    }
                }
            })
            return func
        return decorator

    def get_tool(self, name: str) -> Callable:
        return self.tools.get(name)

    def get_schemas(self) -> List[Dict[str, Any]]:
        return self.schemas

    def execute(self, tool_name: str, **kwargs) -> str:
        """Executes a tool and returns the result as string."""
        func = self.get_tool(tool_name)
        if not func:
            return f"Error: Tool '{tool_name}' not found."
        try:
            result = func(**kwargs)
            return str(result)
        except Exception as e:
            return f"Error executing '{tool_name}': {str(e)}"

# Global tool registry instance for the agent loop
registry = ToolRegistry()
