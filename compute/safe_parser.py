import io
import tokenize
from tokenize import TokenError

import sympy
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations
)

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

ALLOWED_FUNCTIONS = {
    "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
    "sec": sympy.sec, "csc": sympy.csc, "cot": sympy.cot,
    "asin": sympy.asin, "acos": sympy.acos, "atan": sympy.atan,
    "sinh": sympy.sinh, "cosh": sympy.cosh, "tanh": sympy.tanh,
    "exp": sympy.exp, "log":sympy.log, "ln": sympy.log,
    "sqrt": sympy.sqrt, "abs": sympy.Abs,
}
ALLOWED_CONSTANTS = {"pi": sympy.pi, "e": sympy.E}
ALLOWED_OPERATORS = {"+", "-", "*", "/", "^", "**", "(", ")", ","}
IGNORED_TOKENS = {
    tokenize.NEWLINE, tokenize.NL, tokenize.ENDMARKER,
    tokenize.INDENT, tokenize.DEDENT,
}

class UnsafeExpressionError(ValueError):
    pass

def _check_tokens(expression: str) -> None:
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(expression).readline))
    except (TokenError, SyntaxError) as exc:
        raise UnsafeExpressionError("Malformed expression.") from exc

    for tok in tokens:
        if tok.type in IGNORED_TOKENS or tok.type == tokenize.NUMBER:
            continue
        if tok.type == tokenize.OP and tok.string in ALLOWED_OPERATORS:
            continue
        if tok.type == tokenize.NAME and (
            tok.string in ALLOWED_FUNCTIONS
            or tok.string in ALLOWED_CONSTANTS
            or (len(tok.string) == 1 and tok.string.isascii() and tok.string.isalpha())
        ):
            continue
        raise UnsafeExpressionError(f"'{tok.string}' is not allowed.")

def safe_parse(expression: str) -> sympy.Expr:
    _check_tokens(expression)

    local_dict = {**ALLOWED_FUNCTIONS, **ALLOWED_CONSTANTS}
    global_dict = {
        "__builtins__": {},
        "Symbol": sympy.Symbol,
        "Integer": sympy.Integer,
        "Float": sympy.Float,
        "Rational": sympy.Rational,
        "Function": sympy.Function,
    }
    try:
        result = parse_expr(
            expression,
            local_dict=local_dict,
            global_dict=global_dict,
            transformations=TRANSFORMATIONS,
        )
    except (SyntaxError, TokenError, TypeError, NameError) as exc:
        raise UnsafeExpressionError("Could not parse the expression.") from exc

    if not isinstance(result, sympy.Expr):
        raise UnsafeExpressionError("Not a mathematical expression.")
    return result