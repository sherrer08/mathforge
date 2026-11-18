from fastapi import FastAPI
import sympy

app = FastAPI(title="MathForge Compute")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "compute",
        "sympy": sympy.__version__,
    }