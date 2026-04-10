from .registry import registry
import ast
import operator

# Safe math operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.BitXor: operator.xor,
    ast.USub: operator.neg
}

def eval_expr(node):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return OPERATORS[type(node.op)](eval_expr(node.left), eval_expr(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return OPERATORS[type(node.op)](eval_expr(node.operand))
    else:
        raise TypeError(node)

@registry.register(
    name="calculator",
    description="Evaluates a mathematical expression and returns the result. Use this for all math operations.",
    parameters={
        "expression": {
            "type": "string",
            "description": "The mathematical expression to evaluate (e.g., '2 + 2 * 3')."
        }
    }
)
def calculate(expression: str) -> str:
    """Safely evaluate math expressions."""
    try:
        # ast.parse guarantees syntax validity, eval_expr restricts to purely math nodes
        node = ast.parse(expression, mode='eval').body
        result = eval_expr(node)
        return str(result)
    except Exception as e:
        return f"Math Error: Could not evaluate expression '{expression}'. Details: {str(e)}"
