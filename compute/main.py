from tokenize import TokenError

import sympy
from fastapi import FastAPI, HTTPException
from sympy import Symbol, diff, latex
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from models import DifferentiateRequest, MathResult

app = FastAPI(title="MathForge Compute")

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "compute", "sympy": sympy.__version__}

@app.post("/differentiate", response_model=MathResult)
def differentiate(req: DifferentiateRequest):
    try:
        expr = parse_expr(req.expression, transformations=TRANSFORMATIONS)
    except (SyntaxError, TokenError, TypeError):
        raise HTTPException(status_code=400, detail="Could not parse the expression.")

    var = Symbol(req.variable)
    result = diff(expr, var, req.order)

    return MathResult(
        input_latex=latex(expr),
        result=str(result),
        result_latex=latex(result)
    )