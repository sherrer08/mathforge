import pytest
import sympy

from safe_parser import UnsafeExpressionError, safe_parse

x = sympy.Symbol("x")

@pytest.mark.parametrize("text, expected", [
    ("x^2", x**2),
    ("3x^3 - 2x", 3 * x**3 - 2 * x),
    ("sin x", sympy.sin(x)),
    ("(x+1)(x-1)", (x + 1) * (x - 1)),
    ("e^x", sympy.exp(x)),
    ("ln(x)", sympy.log(x)),
    ("sqrt(x) + pi", sympy.sqrt(x) + sympy.pi),
    ("oo", sympy.oo),
])
def test_valid_math_parses(text, expected):
    result = safe_parse(text)
    assert result == expected or sympy.simplify(safe_parse(text) - expected) == 0

@pytest.mark.parametrize("attack", [
    "__import__('builtins').print('pwned')",
    "x.__class__",
    "().__class__.__base__.__subclasses__()",
    "[x]",
    "lambda: 1",
    "'text'",
    "x; 1",
    "x = 1",
    "eval(x)",
    "exec",
    "Symbol('x')",
    "x if 1 else 2",
    "\uff58"
])
def test_attacks_are_rejected(attack):
    with pytest.raises(UnsafeExpressionError):
        safe_parse(attack)

@pytest.mark.parametrize("bad", ["sin(x", "xsin(x)", "x, y"])
def test_non_math_is_rejected(bad):
    with pytest.raises(UnsafeExpressionError):
        safe_parse(bad)