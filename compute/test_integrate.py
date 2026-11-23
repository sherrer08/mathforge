import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def post(body):
    return client.post("/integrate", json=body)


def test_indefinite_adds_constant():
    r = post({"expression": "x^2"})
    assert r.status_code == 200
    assert r.json()["result"] == "x**3/3 + C"
    assert r.json()["result_latex"].endswith("+ C")


@pytest.mark.parametrize("expression, lower, upper, expected", [
    ("x^2", "0", "1", "1/3"),
    ("sin(x)", "0", "pi", "2"),
    ("e^(-x)", "0", "oo", "1"),
    ("e^(-x^2)", "-oo", "oo", "sqrt(pi)"),
])
def test_definite(expression, lower, upper, expected):
    r = post({"expression": expression, "lower": lower, "upper": upper})
    assert r.status_code == 200
    assert r.json()["result"] == expected


@pytest.mark.parametrize("expression, lower, upper", [
    ("1/x", "1", "oo"),
    ("1/x", "-1", "1"),
])
def test_divergent_returns_422(expression, lower, upper):
    r = post({"expression": expression, "lower": lower, "upper": upper})
    assert r.status_code == 422
    assert "does not converge" in r.json()["detail"]


def test_no_closed_form_returns_422():
    r = post({"expression": "x^x"})
    assert r.status_code == 422
    assert "closed-form" in r.json()["detail"]


def test_one_bound_only_returns_422():
    assert post({"expression": "x", "lower": "0"}).status_code == 422


def test_injection_in_bound_returns_400():
    r = post({"expression": "x", "lower": "0", "upper": "__import__('os')"})
    assert r.status_code == 400