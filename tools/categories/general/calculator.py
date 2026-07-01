import ast
import operator

from langchain.tools import tool

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Espressione non valida")


@tool
def calculator(expression: str) -> str:
    """Calcola il risultato di un'espressione matematica (es. '12 * (3 + 4) / 2').
    Supporta solo numeri e operatori +, -, *, /, **, %. Usa questo tool per
    qualsiasi calcolo numerico invece di farlo a mente."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval(tree.body)
        return str(result)
    except Exception:
        return "Espressione non valida o non supportata."