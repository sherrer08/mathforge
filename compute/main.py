import sympy
from fastapi import FastAPI, HTTPException

from models import DifferentiateRequest, IntegrateRequest, LimitRequest, MathResult
from safe_parser import UnsafeExpressionError
from sandbox import ComputationFailed, ComputationTimeout, run_limited
from tasks import MathError, differentiate_task, integrate_task, limit_task

app = FastAPI(title="MathForge Compute")

def run_task(task, *args) -> dict:
    try:
        return run_limited(task, *args)
    except UnsafeExpressionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except MathError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except ComputationTimeout:
        raise HTTPException(status_code=422, detail="This problem took too long to solve.")
    except ComputationFailed as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@app.get("/health")
def health():
    return {"status": "ok", "service": "compute", "sympy": sympy.__version__}

@app.post("/differentiate", response_model=MathResult)
def differentiate(req: DifferentiateRequest):
    return run_task(differentiate_task, req.expression, req.variable, req.order)

@app.post("/integrate", response_model=MathResult)
def integrate(req: IntegrateRequest):
    return run_task(integrate_task, req.expression, req.variable, req.lower, req.upper)

@app.post("/limit", response_model=MathResult)
def limit(req: LimitRequest):
    return run_task(limit_task, req.expression, req.variable, req.point, req.direction)