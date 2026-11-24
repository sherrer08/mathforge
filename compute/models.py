from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

Entry = Annotated[str, Field(min_length=1, max_length=50)]
Row = Annotated[list[Entry], Field(min_length=1, max_length=5)]

SQUARE_ONLY = {"determinant", "inverse", "eigenvalues"}

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

class MatrixRequest(BaseModel):
    matrix: list[Row] = Field(min_length=1, max_length=5, examples=[[["1", "2"], ["3", "4"]]])
    operation: Literal["determinant", "inverse", "rref", "eigenvalues", "transpose"]

    @model_validator(mode="after")
    def check_shape(self):
        width = len(self.matrix[0])
        if any(len(row) != width for row in self.matrix):
            raise ValueError("All rows must have the same number of entries.")
        if self.operation in SQUARE_ONLY and len(self.matrix) != width:
            raise ValueError(f"'{self.operation}' requires a matrix.")
        return self

class MathResult(BaseModel):
    input_latex: str
    result: str
    result_latex: str