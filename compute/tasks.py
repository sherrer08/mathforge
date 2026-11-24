import sympy
from sympy import AccumBounds, Integral, Symbol, Limit, diff, integrate, limit, latex

from safe_parser import UnsafeExpressionError, safe_parse

NOT_FINITE = (sympy.oo, -sympy.oo, sympy.zoo, sympy.nan)

UNDEFINED = (sympy.zoo, sympy.nan)

SIMPLIFY_OPERATIONS = {
    "simplify": sympy.simplify,
    "expand": sympy.expand,
    "factor": sympy.factor,
}

class MathError(ValueError):
    pass

def differentiate_task(expression: str, variable: str, order: int) -> dict:
    expr = safe_parse(expression)
    result = diff(expr, Symbol(variable), order)
    return {
        "input_latex": latex(expr),
        "result": str(result),
        "result_latex": latex(result),
    }

def integrate_task(expression: str, variable: str, lower: str | None, upper: str | None) -> dict:
    expr = safe_parse(expression)
    var = Symbol(variable)

    if lower is None:
        result = integrate(expr, var)
        if result.has(Integral):
            raise MathError("No closed-form antiderivative was found.")
        return {
            "input_latex": latex(Integral(expr, var)),
            "result": f"{result} + C",
            "result_latex": f"{latex(result)} + C",
        }

    a, b = safe_parse(lower), safe_parse(upper)
    result = integrate(expr, (var, a, b))
    if result.has(Integral):
        raise MathError("This integral could not be evaluated exactly.")
    if result.has(*NOT_FINITE):
        raise MathError("This integral does not converge.")
    return {
        "input_latex": latex(Integral(expr, (var, a, b))),
        "result": str(result),
        "result_latex": latex(result),
    }

def limit_task(expression: str, variable: str, point: str, direction: str) -> dict:
    expr = safe_parse(expression)
    var = Symbol(variable)
    at = safe_parse(point)

    try:
        result = limit(expr, var, at, dir=direction)
    except ValueError as exc:
        raise MathError("This limit does not exist.") from exc

    if result.has(Limit):
        raise MathError("This limit could not be evaluated.")
    if result.has(AccumBounds) or result.has(*UNDEFINED):
        raise MathError("This limit does not exist.")

    return {
        "input_latex": latex(Limit(expr, var, at, dir=direction)),
        "result": str(result),
        "result_latex": latex(result),
    }

def solve_task(expression: str, variable: str) -> dict:
    sides = expression.split("=")
    if len(sides) > 2:
        raise UnsafeExpressionError("An equation can contain at most one '='.")

    lhs = safe_parse(sides[0])
    rhs = safe_parse(sides[1]) if len(sides) == 2 else sympy.Integer(0)
    var = Symbol(variable)

    try:
        solutions = sympy.solveset(lhs - rhs, var, domain=sympy.S.Reals)
    except NotImplementedError as exc:
        raise MathError("This equation could not be solved exactly.") from exc

    if solutions.has(sympy.ConditionSet):
        raise MathError("This equation could not be solved exactly.")

    if solutions == sympy.S.EmptySet:
        result, result_latex = "No real solutions", r"\varnothing"
    elif solutions == sympy.S.Reals:
        result, result_latex = "All real numbers", r"\mathbb{R}"
    else:
        result, result_latex = str(solutions), latex(solutions)

    return {
        "input_latex": latex(sympy.Eq(lhs, rhs, evaluate=False)),
        "result": result,
        "result_latex": result_latex,
    }

def simplify_task(expression: str, operation: str) -> dict:
    expr = safe_parse(expression)
    op = SIMPLIFY_OPERATIONS[operation]
    result = op(expr)
    return {
        "input_latex": latex(expr),
        "result": str(result),
        "result_latex": latex(result),
    }

def _format_eigenvalues(eigenvalues: dict) -> tuple[str, str]:
    text = ", ".join(
        f"{value} (multiplicity {count})" if count > 1 else str(value)
        for value, count in eigenvalues.items()
    )
    tex = r"\lambda = " + ", ".join(latex(value) for value in eigenvalues)
    return text, tex

def matrix_task(matrix: list[list[str]], operation: str) -> dict:
    m = sympy.Matrix([[safe_parse(entry) for entry in row] for row in matrix])
    shown = latex(m)

    if operation == "determinant":
        result = m.det()
        input_latex = rf"\det {shown}"
    elif operation == "inverse":
        try:
            result = m.inv()
        except ValueError as exc:
            raise MathError("This matrix is not invertible.") from exc
        input_latex = rf"{shown}^{{-1}}"
    elif operation == "rref":
        result, _pivots = m.rref()
        input_latex = rf"\operatorname{{rref}} {shown}"
    elif operation == "transpose":
        result = m.T
        input_latex = rf"{shown}^{{T}}"
    elif operation == "eigenvalues":
        text, tex = _format_eigenvalues(m.eigenvals())
        return {
            "input_latex": rf"\operatorname{{eig}} {shown}",
            "result": text,
            "result_latex": tex,
        }

    return {
        "input_latex": input_latex,
        "result": str(result),
        "result_latex": latex(result),
    }