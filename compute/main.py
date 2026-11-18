from tokenize import TokenError

import sympy
from fastapi import FastAPI, HTTPException
from sympy import Symbol, diff, latex
from safe_parser import UnsafeExpressionError, safe_parse

from models import DifferentiateRequest, MathResult

app = FastAPI(title="MathForge Compute")

@app.get("/health")
def health():
    return {"status": "ok", "service": "compute", "sympy": sympy.__version__}

@app.post("/differentiate", response_model=MathResult)
def differentiate(req: DifferentiateRequest):
    try:
        expr = safe_parse(req.expression)
    except UnsafeExpressionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    var = Symbol(req.variable)
    result = diff(expr, var, req.order)

    return MathResult(
        input_latex=latex(expr),
        result=str(result),
        result_latex=latex(result)
    )