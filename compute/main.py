import sympy
from fastapi import FastAPI, HTTPException

from models import DifferentiateRequest, MathResult
from safe_parser import UnsafeExpressionError
from sandbox import ComputationFailed, ComputationTimeout, run_limited
from tasks import differentiate_task

from models import DifferentiateRequest, MathResult

app = FastAPI(title="MathForge Compute")

@app.get("/health")
def health():
    return {"status": "ok", "service": "compute", "sympy": sympy.__version__}

@app.post("/differentiate", response_model=MathResult)
def differentiate(req: DifferentiateRequest):
    try:
        return run_limited(differentiate_task, req.expression, req.variable, req.order)
    except UnsafeExpressionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ComputationTimeout:
        raise HTTPException(status_code=422, detail="This problem took too long to solve.")
    except ComputationFailed as exc:
        raise HTTPException(status_code=422, detail=str(exc))