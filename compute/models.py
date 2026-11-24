from typing import Literal

from pydantic import BaseModel, Field, model_validator

class ExpressionRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=200, examples=["x^2 * sin(x)"])
    variable: str = Field(default="x", pattern=r"^[a-zA-Z]$")

class DifferentiateRequest(ExpressionRequest):
    order: int = Field(default=1, ge=1, le=10)

class IntegrateRequest(ExpressionRequest):
    lower: str | None = Field(default=None, min_length=1, max_length=50, examples=["0"])
    upper: str | None = Field(default=None, min_length=1, max_length=50, examples=["1"])

    @model_validator(mode="after")
    def both_bounds_or_neither(self):
        if (self.lower is None) != (self.upper is None):
            raise ValueError("Provide both lower and upper bounds, or neither.")
        return self

class LimitRequest(ExpressionRequest):
    point: str = Field(min_length=1, max_length=50, examples=["0"])
    direction: Literal["+", "-", "+-"] = "+-"

class SolveRequest(ExpressionRequest):
    expression: str = Field(min_length=1, max_length=200, examples=["x^2 = 4"])

class SimplifyRequest(ExpressionRequest):
    operation: Literal["simplify", "expand", "factor"] = "simplify"

class MathResult(BaseModel):
    input_latex: str
    result: str
    result_latex: str