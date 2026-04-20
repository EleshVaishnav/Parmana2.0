from .registry import registry
import traceback
import sys
from io import StringIO

@registry.register(
    name="execute_python_code",
    description="Executes a raw python script sandbox to evaluate data.",
    parameters={
        "code": {"type": "string", "description": "Python code to execute"}
    }
)
def execute_python_code(code: str) -> str:
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    try:
        exec(code, {})
        sys.stdout = old_stdout
        return f"Execution Success. Output:\n{redirected_output.getvalue()}"
    except Exception as e:
        sys.stdout = old_stdout
        return f"Execution Error:\n{traceback.format_exc()}"
