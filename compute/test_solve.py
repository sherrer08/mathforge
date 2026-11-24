import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def post(expression, variable="x"):
    return client.post("/solve", json={"expression": expression, "variable": variable})


@pytest.mark.parametrize("expression, expected", [
    ("x^2 = 4", "{-2, 2}"),
    ("x^2 - 4", "{-2, 2}"),
    ("2x + 3 = 7", "{2}"),
    ("x^2 - 2x + 1 = 0", "{1}"),
])
def test_finite_solutions(expression, expected):
    r = post(expression)
    assert r.status_code == 200
    assert r.json()["result"] == expected


def test_periodic_solutions_are_not_truncated():
    r = post("sin(x) = 0")
    assert r.status_code == 200
    assert r.json()["result"] != "{0, pi}"
    assert r"n \in \mathbb{Z}" in r.json()["result_latex"]


def test_no_real_solutions_is_an_answer():
    r = post("x^2 + 1 = 0")
    assert r.status_code == 200
    assert r.json()["result"] == "No real solutions"


def test_identity_is_all_real_numbers():
    r = post("x - x = 0")
    assert r.status_code == 200
    assert r.json()["result"] == "All real numbers"
    assert "True" not in r.json()["input_latex"]


def test_unsolvable_returns_422():
    assert post("x^x = 2").status_code == 422


def test_two_equals_signs_returns_400():
    assert post("x = 1 = 2").status_code == 400


def test_injection_on_right_side_returns_400():
    r = post("x = __import__('os')")
    assert r.status_code == 400
    assert "__import__" in r.json()["detail"]