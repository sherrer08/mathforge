from sympy import Symbol, diff, latex

from safe_parser import safe_parse

def differentiate_task(expression: str, variable: str, order: int) -> dict:
    expr = safe_parse(expression)
    result = diff(expr, Symbol(variable), order)
    return {
        "input_latex": latex(expr),
        "result": str(result),
        "result_latex": latex(result),
    }