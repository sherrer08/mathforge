import sympy
from sympy import Integral, Symbol, diff, integrate, latex

from safe_parser import safe_parse

NOT_FINITE = (sympy.oo, -sympy.oo, sympy.zoo, sympy.nan)

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
            raise MathError("No closed-form anitderivative was found.")
        return {
            "input_latex": latex(Integral(expr, var)),
            "result": f"{result} + C",
            "result_latex": f"{latex(result)} + C",
        }

    a, b =safe_parse(lower), safe_parse(upper)
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