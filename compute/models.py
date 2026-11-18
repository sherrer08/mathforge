from pydantic import BaseModel, Field

class DifferentiateRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=200, examples=["x^2 * sin(x)"])
    variable: str = Field(default="x", pattern=r"^[a-zA-Z]$")
    order: int = Field(default=1, ge=1, le=10)

class MathResult(BaseModel):
    input_latex: str
    result: str
    result_latex: str