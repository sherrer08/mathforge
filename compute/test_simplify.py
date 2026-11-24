import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def post(body):
    return client.post("/simplify", json=body)


@pytest.mark.parametrize("expression, operation, expected", [
    ("sin(x)^2 + cos(x)^2", "simplify", "1"),
    ("(x^2 - 1)/(x - 1)", "simplify", "x + 1"),
    ("(x+1)^2", "expand", "x**2 + 2*x + 1"),
    ("x^2 - 4", "factor", "(x - 2)*(x + 2)"),
])
def test_operations(expression, operation, expected):
    r = post({"expression": expression, "operation": operation})
    assert r.status_code == 200
    assert r.json()["result"] == expected


def test_default_operation_is_simplify():
    r = post({"expression": "sin(x)^2 + cos(x)^2"})
    assert r.status_code == 200
    assert r.json()["result"] == "1"


@pytest.mark.parametrize("expression, operation", [
    ("x^2 + 1", "factor"),   # can't be factored over the rationals
    ("x", "simplify"),       # already as simple as possible
])
def test_already_simplest_form_is_returned_unchanged(expression, operation):
    r = post({"expression": expression, "operation": operation})
    assert r.status_code == 200
    assert r.json()["result"] == expression.replace("^", "**")


def test_unknown_operation_returns_422():
    r = post({"expression": "x", "operation": "differentiate"})
    assert r.status_code == 422


def test_injection_returns_400():
    r = post({"expression": "__import__('os')", "operation": "expand"})
    assert r.status_code == 400