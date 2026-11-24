import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def post(matrix, operation):
    return client.post("/matrix", json={"matrix": matrix, "operation": operation})


@pytest.mark.parametrize("matrix, operation, expected", [
    ([["1", "2"], ["3", "4"]], "determinant", "-2"),
    ([["x", "1"], ["1", "x"]], "determinant", "x**2 - 1"),
    ([["1", "2"], ["3", "4"]], "inverse", "Matrix([[-2, 1], [3/2, -1/2]])"),
    ([["1", "2", "3"], ["4", "5", "6"]], "rref", "Matrix([[1, 0, -1], [0, 1, 2]])"),
    ([["1", "2", "3"], ["4", "5", "6"]], "transpose", "Matrix([[1, 4], [2, 5], [3, 6]])"),
    ([["2", "0"], ["0", "3"]], "eigenvalues", "2, 3"),
    ([["2", "1"], ["0", "2"]], "eigenvalues", "2 (multiplicity 2)"),
    ([["0", "-1"], ["1", "0"]], "eigenvalues", "-I, I"),
])
def test_operations(matrix, operation, expected):
    r = post(matrix, operation)
    assert r.status_code == 200
    assert r.json()["result"] == expected


def test_singular_inverse_returns_422():
    r = post([["1", "2"], ["2", "4"]], "inverse")
    assert r.status_code == 422
    assert "not invertible" in r.json()["detail"]


@pytest.mark.parametrize("matrix, operation", [
    ([["1", "2"], ["3"]], "transpose"),                   # ragged rows
    ([["1", "2", "3"], ["4", "5", "6"]], "determinant"),  # not square
    ([["1"] * 6] * 6, "transpose"),                       # larger than 5x5
    ([], "transpose"),                                    # empty matrix
    ([["1", ""], ["3", "4"]], "transpose"),               # empty entry
])
def test_invalid_shapes_return_422(matrix, operation):
    assert post(matrix, operation).status_code == 422


def test_unknown_operation_returns_422():
    assert post([["1"]], "multiply").status_code == 422


def test_injection_in_entry_returns_400():
    r = post([["1", "__import__('os')"], ["3", "4"]], "determinant")
    assert r.status_code == 400